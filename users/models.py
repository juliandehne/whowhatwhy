from django.db import models
from django.contrib.auth.models import User

from delab.delab_enums import LANGUAGE
from util.pictures import resize_picture


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    primary_language = models.TextField(default=LANGUAGE.ENGLISH, choices=LANGUAGE.choices,
                                        help_text="The primary working language you are proficient in.")
    secondary_language = models.TextField(default=LANGUAGE.GERMAN, choices=LANGUAGE.choices,
                                          help_text="The second working language you are proficient in.", null=True,
                                          blank=True)
    tertiary_language = models.TextField(choices=LANGUAGE.choices,
                                         help_text="The third working language you are proficient in.", null=True,
                                         blank=True)
    full_name = models.TextField(blank=True, null=True, help_text="Name of the account owner! Needs to be the correct name for payment")
    iban = models.TextField(blank=True, null=True, help_text="The IBAN for your remuneration")
    birthday = models.DateField(null=True, blank=True, help_text="your birthday")
    billing_address = models.TextField(null=True, blank=True, help_text="your current living address")

    agb = models.BooleanField(blank=True, null=True, help_text="Please check this to affirm that we can store your "
                                                               "payment detail for the duration of the study. The "
                                                               "information will only be used for the purpose of "
                                                               "remuneration in the context of this study and will be "
                                                               "deleted afterwards!")

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_picture(self)
