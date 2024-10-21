from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver




def product_images_directory_path(instance:'User', filename: str):
    return 'users/user_{pk}/images/{filename}'.format(pk=instance.user.pk, filename=filename)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_exepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=product_images_directory_path, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

