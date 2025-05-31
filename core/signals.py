from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Vocabulary, VocabularyEntry


@receiver(post_save, sender=Vocabulary)
def sync_vocabulary_entry(sender, instance, **kwargs):
    """Automatically sync Vocabulary changes to VocabularyEntry"""
    if instance.is_correct and instance.language in ['ar', 'he']:
        try:
            # Get the other language translation
            other_lang = 'he' if instance.language == 'ar' else 'ar'
            other_trans = Vocabulary.objects.get(
                concept=instance.concept,
                language=other_lang,
                is_correct=True
            )

            # Prepare update data
            update_data = {
                'hint': instance.hint or other_trans.hint or '',
                f'{instance.language}_text': instance.text,
                f'{other_lang}_text': other_trans.text
            }

            # Update or create VocabularyEntry
            VocabularyEntry.objects.update_or_create(
                concept=instance.concept,
                defaults=update_data
            )
        except Vocabulary.DoesNotExist:
            pass  # Wait until both translations exist
        except Exception as e:
            print(f"Error syncing VocabularyEntry: {str(e)}")