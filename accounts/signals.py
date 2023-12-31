# Django Signals
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # User profile does not exist, create one
            UserProfile.objects.create(user=instance)


@receiver(pre_save, sender=User)
def pre_save_receiver(sender, instance, **kwargs):
    pass