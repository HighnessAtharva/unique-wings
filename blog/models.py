from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class BlogPost(models.Model):
    """
    Model for a blog Post
    """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=150)
    info = models.CharField(
        max_length=254,
        null=True, blank=True)
    content = models.TextField(
        null=False, blank=False)
    image = models.ImageField(
        null=True, blank=True)
    date_posted = models.DateField(
        auto_now_add=True)

    def __str__(self):
        return f'{self.title} | {str(self.author)}'


class BlogComment(models.Model):
    """
    Model allows user to add comment to blog
    """
    blogpost = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments')
    user_comment = models.ForeignKey(
        User, on_delete=models.CASCADE)
    date = models.DateTimeField(
        auto_now_add=True)
    comment = models.TextField(
        max_length=1024,
        null=False, blank=False)

    def __str__(self):
        return self.comment
