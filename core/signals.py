from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, CourseDocument

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:

        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not kwargs.get('created') and hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=CourseDocument)
def index_on_upload(sender, instance, created, **kwargs):
    # Only index on first save (creation). Re-indexing on every edit would be
    # wasteful since the file itself doesn't change after upload.
    if not created:
        return
    try:
        from .services.assistant import index_document
        index_document(
            course_id=instance.course_id,
            document_id=instance.id,
            file_path=instance.file.path,
            title=instance.title,
        )
    except Exception as e:
        # Log but don't crash the upload — the file is saved; indexing can be
        # retried later with: python manage.py index_documents
        import logging
        logging.getLogger(__name__).error(
            "Failed to index document %s (course %s): %s",
            instance.id, instance.course_id, e,
        )


@receiver(post_delete, sender=CourseDocument)
def remove_on_delete(sender, instance, **kwargs):
    # Remove this document's vectors from ChromaDB when the doc is deleted.
    try:
        from .services.assistant import _get_vectorstore
        vs = _get_vectorstore(instance.course_id)
        vs._collection.delete(where={"document_id": instance.id})
    except Exception:
        pass