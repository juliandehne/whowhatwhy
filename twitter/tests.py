from django.test import TestCase
from blog.models import Post
import logging


# Create your tests here.
class TwitterSandbox(TestCase):

    def test_print_first_blog_title(self):
        logger = logging.getLogger('django_test')
        #logger.info(Post.objects.first().title)
