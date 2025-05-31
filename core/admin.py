from django.contrib import admin
from .models import VocabularyEntry, Word

@admin.register(VocabularyEntry)
class VocabularyEntryAdmin(admin.ModelAdmin):
    list_display = ['arabic_text']
    fields = ['arabic_text', 'gif']

admin.site.register(Word)
