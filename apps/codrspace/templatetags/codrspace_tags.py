from django.template import Library, TemplateSyntaxError, Variable, Node
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from codrspace.models import Post

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


@register.inclusion_tag("lastest_posts.html", takes_context=True)
def latest_posts(context, amount):
    posts = Post.objects.filter(status="published").order_by('-pk')
    if posts:
        posts = posts[:int(amount)]
    context.update({
        'posts': posts
    })
    return context
