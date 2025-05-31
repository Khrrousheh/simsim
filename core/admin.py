from django.contrib import admin
from .models import VocabularyEntry, Word
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class VocabularyEntryResource(resources.ModelResource):
    class Meta:
        model = VocabularyEntry
        fields = ('id', 'arabic_text', 'gif')  # adjust as needed

@admin.register(VocabularyEntry)
class VocabularyEntryAdmin(ImportExportModelAdmin):
    resource_class = VocabularyEntryResource
    list_display = ['arabic_text']
    fields = ['arabic_text', 'gif']

admin.site.register(Word)
