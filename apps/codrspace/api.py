from django import VERSION
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned

from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import CleanedDataFormValidation
from tastypie import fields
from tastypie.exceptions import NotFound, Unauthorized
from tastypie.utils import dict_strip_unicode_keys
from tastypie import http

from codrspace.forms import APIPostForm
from codrspace.models import Post


class CodrspaceModelResource(ModelResource):
    def put_detail(self, request, **kwargs):
        """Override put_detail so that it doesn't create a new resource when
        One doesn't exists, I don't like this reflex"""
        if VERSION >= (1, 4):
            body = request.body
        else:
            body = request.raw_post_data
        deserialized = self.deserialize(request, body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)

        try:
            updated_bundle = self.obj_update(bundle=bundle, **self.remove_api_resource_names(kwargs))

            if not self._meta.always_return_data:
                return http.HttpNoContent()
            else:
                updated_bundle = self.full_dehydrate(updated_bundle)
                updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
                return self.create_response(request, updated_bundle, response_class=http.HttpAccepted)
        except (NotFound, MultipleObjectsReturned):
            raise NotFound("A model instance matching the provided arguments could not be found.")


class CodrspaceAuthorization(Authorization):
    """Authorization based on request user"""
    def delete_list(self, object_list, bundle):
        raise Unauthorized('Cannot delete a list of posts')

    def delete_detail(self, object_list, bundle):
        if bundle.obj.author == bundle.request.user:
            return True
        return False

    def read_list(self, object_list, bundle):
        return object_list.filter(author=bundle.request.user)

    def read_detail(self, object_list, bundle):
        """read_detail will handle the update_detail permissions"""
        if bundle.obj.author == bundle.request.user:
            return True
        return False

    def update_list(self, object_list, bundle):
        raise Unauthorized('Cannot update a list of posts')


class PostValidation(CleanedDataFormValidation):
    """Form validation for a post"""
    def is_valid(self, bundle, request=None):
        """Adds request.user to the form class before validation"""
        form_args = self.form_args(bundle)
        form_args.update({'user': request.user})

        form = self.form_class(**form_args)

        if form.is_valid():
            return {}

        # The data is invalid. Let's collect all the error messages & return them.
        return form.errors


class PostResource(CodrspaceModelResource):
    # make sure these don't get set. The Django
    # model system will take care of it
    create_dt = fields.DateTimeField(attribute='create_dt', readonly=True)
    update_dt = fields.DateTimeField(attribute='update_dt', readonly=True)

    class Meta:
        resource_name = 'post'
        queryset = Post.objects.all()
        queryset = queryset.order_by('-publish_dt')
        allowed_methods = ['get', 'put', 'delete', 'post']
        authentication = ApiKeyAuthentication()
        authorization = CodrspaceAuthorization()
        serializer = Serializer(formats=['json'])
        validation = PostValidation(form_class=APIPostForm)
        always_return_data = True

    def dehydrate(self, bundle):
        bundle.data['url'] = bundle.obj.url()
        return bundle

    def hydrate(self, bundle, request=None):
        # set the status if it is not specified
        if not bundle.obj.status:
            bundle.obj.status = "draft"

        # automatically set the author
        bundle.obj.author = User.objects.get(pk=bundle.request.user.id)

        return bundle
