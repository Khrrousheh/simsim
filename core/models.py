from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator



class VocabularyEntry(models.Model):
    concept = models.CharField(max_length=100)
    hint = models.TextField(blank=True)
    arabic_text = models.CharField(max_length=255)
    hebrew_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Vocabulary Entries"
        ordering = ['concept']

    def __str__(self):
        return self.concept

    def get_quiz_options(self, language='he', count=4):
        """Helper for API to get question + options"""
        from django.db.models import Q
        correct = self.words.filter(language=language, is_correct=True).first()
        incorrect = list(self.words.filter(
            Q(language=language) & Q(is_correct=False)
        ).exclude(text=correct.text))

        options = [correct] + random.sample(incorrect, min(count - 1, len(incorrect)))
        random.shuffle(options)
        return {
            'question': self.arabic_text,
            'options': [{'id': w.id, 'text': w.text} for w in options],
            'correct_id': correct.id
        }


class Vocabulary(models.Model):
    LANGUAGES = [
        ('ar', 'Arabic'),
        ('he', 'Hebrew'),
        ('en', 'English')
    ]

    concept = models.CharField(max_length=100, db_index=True)
    language = models.CharField(max_length=2, choices=LANGUAGES)
    text = models.CharField(max_length=255)
    hint = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('concept', 'language')
        verbose_name_plural = "Vocabulary"

    def __str__(self):
        return f"{self.concept} ({self.get_language_display()})"

    def clean(self):
        super().clean()

        # Skip validation for English or non-correct translations
        if self.language != 'he' or not self.is_correct:
            return

        try:
            arabic_entry = Vocabulary.objects.get(
                concept=self.concept,
                language='ar',
                is_correct=True
            )
            arabic_length = len(arabic_entry.text.strip())
            hebrew_length = len(self.text.strip())

            if arabic_length != hebrew_length:
                raise ValidationError(
                    f"Hebrew text length ({hebrew_length}) must match Arabic text length ({arabic_length}) "
                    f"for concept '{self.concept}'"
                )
        except Vocabulary.DoesNotExist:
            raise ValidationError(
                f"Corresponding Arabic entry not found for concept '{self.concept}'"
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Runs clean() validation
        super().save(*args, **kwargs)

class GameSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    language_preference = models.CharField(max_length=2, choices=Vocabulary.LANGUAGES, default='he')


class GameResponse(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='responses')
    concept = models.CharField(max_length=100)
    selected_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    response_time_ms = models.PositiveIntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['session', 'submitted_at']),
            models.Index(fields=['is_correct']),
        ]
