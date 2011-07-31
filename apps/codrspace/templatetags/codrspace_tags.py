from django.template import Library, TemplateSyntaxError, Variable, Node
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

register = Library()


class RandomBlogNode(Node):
    def render(self, context):
        random_user = User.objects.order_by('?')[0]
        return reverse('post_list', args=[random_user.username])

@register.tag
def random_blog(parser, token):
    """
    Get a random bloggers post list page
    {% random_blog %}
    """
    return RandomBlogNode()
