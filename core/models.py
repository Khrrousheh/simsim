from django.db import models
from django.core.exceptions import ValidationError

class VocabularyEntry(models.Model):
    arabic_text = models.CharField(max_length=255)
    gif = models.ImageField(upload_to='gifs/', blank=True, null=True)

    def __str__(self):
        return self.arabic_text

class Word(models.Model):
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=[('he', 'Hebrew'), ('ar', 'Arabic')])
    entry = models.ForeignKey('VocabularyEntry', on_delete=models.CASCADE, related_name='words')

    def __str__(self):
        return self.text

    def clean(self):
        super().clean()

        if self.is_correct:
            arabic_length = len(self.entry.arabic_text.strip())
            hebrew_length = len(self.text.strip())

            if arabic_length != hebrew_length:
                raise ValidationError(
                    f"The Hebrew word must be the same length as the Arabic word "
                    f"(Arabic: {arabic_length}, Hebrew: {hebrew_length})."
                )

class Answer(models.Model):
    entry = models.ForeignKey(VocabularyEntry, on_delete=models.CASCADE)
    selected_word = models.ForeignKey(Word, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'✅' if self.is_correct else '❌'} {self.selected_word.text}"
    
class PlayerScore(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.score}"
