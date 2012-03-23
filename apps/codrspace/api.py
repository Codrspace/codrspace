from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from codrspace.models import Post


class PostResource(ModelResource):
    class Meta:
        queryset = Post.objects.filter(status='published')
        resource_name = 'post'
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(author=request.user)
