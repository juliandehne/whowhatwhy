from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.urls import reverse

from util.pictures import resize_picture
from django_countries.fields import CountryField


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class Institution(models.Model):
    readonly_fields = ('id',)
    title = models.CharField(max_length=100)
    image = models.ImageField(default='default.jpg', upload_to='institution_pics')
    description = models.TextField()
    country = CountryField(default='DE')
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))

    class Meta:
        constraints = [
            UniqueConstraint(fields=['title'], name="unique_institution_constraint"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('institution-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_picture(self.image)


class Post(models.Model):
    readonly_fields = ('id',)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_picture(self.author.profile.image)
