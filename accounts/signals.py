# Django Signals
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        print('Created')
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # User profile does not exist, create one
            UserProfile.objects.create(user=instance)
            print('Profile do not exist, create new one')
        print('User is updated')


@receiver(pre_save, sender=User)
def pre_save_receiver(sender, instance, **kwargs):
    print(instance.username, "is being created")