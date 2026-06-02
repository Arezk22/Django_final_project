from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Profile
from core.models import Course
from core.services.recommendation_service import index_course 


# ==========================================
# User Signals
# ==========================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create Profile automatically when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Save the related Profile when the User is updated.
    """
    if not created and hasattr(instance, 'profile'):
        instance.profile.save()


# ==========================================
# Course Signals
# ==========================================

@receiver(post_save, sender=Course)
def course_embedding_handler(sender, instance, **kwargs):
    """
    Index published courses for the recommendation system.
    """
    if instance.is_published:
        index_course(instance)