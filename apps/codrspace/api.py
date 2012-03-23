from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from codrspace.models import Post


class PostResource(ModelResource):
    class Meta:
        resource_name = 'post'
        queryset = Post.objects.filter(status='published')
        queryset = queryset.order_by('-publish_dt')
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(author=request.user)

    def dehydrate(self, bundle):
        print dir(bundle)
        bundle.data['url'] = bundle.obj.url()
        return bundle
