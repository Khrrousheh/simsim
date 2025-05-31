from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from core.models import Vocabulary, VocabularyEntry
from django.db import transaction


class Command(BaseCommand):
    help = 'Sync vocabulary from Vocabulary to VocabularyEntry model'

    def handle(self, *args, **options):
        synced = 0
        errors = 0

        concepts = Vocabulary.objects.filter(
            language__in=['ar', 'he'],
            is_correct=True
        ).values_list('concept', flat=True).distinct()

        self.stdout.write(f"Starting sync for {len(concepts)} concepts...")

        for concept in concepts:
            try:
                with transaction.atomic():
                    arabic = Vocabulary.objects.get(
                        concept=concept,
                        language='ar',
                        is_correct=True
                    )
                    hebrew = Vocabulary.objects.get(
                        concept=concept,
                        language='he',
                        is_correct=True
                    )

                    VocabularyEntry.objects.update_or_create(
                        concept=concept,  # Fixed typo here (was 'concept')
                        defaults={
                            'arabic_text': arabic.text,
                            'hebrew_text': hebrew.text,
                            'hint': arabic.hint or hebrew.hint or ''
                        }
                    )
                    synced += 1

            except ObjectDoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Skipping '{concept}' - missing translation")
                )
                errors += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error syncing '{concept}': {str(e)}")
                )
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(f"Sync complete! Success: {synced}, Errors: {errors}")
        )