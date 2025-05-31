from django.contrib import admin
from django.utils.html import format_html
from .models import VocabularyEntry, Vocabulary, GameSession, GameResponse
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse
from django.db import transaction
import csv
from io import TextIOWrapper


class VocabularyInline(admin.TabularInline):
    model = Vocabulary
    extra = 1
    fields = ('text', 'language', 'is_correct', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.language == 'he':
            return format_html('<span style="direction: rtl; font-family: David, Arial; font-size: 16px;">{}</span>',
                               obj.text)
        return obj.text

    preview.short_description = "Styled Preview"


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(VocabularyEntry)
class VocabularyEntryAdmin(admin.ModelAdmin):
    list_display = ('concept', 'arabic_text', 'hebrew_text', 'hint')
    search_fields = ('concept', 'arabic_text', 'hebrew_text')
    list_filter = ('created_at',)
    # inlines = [VocabularyInline]

    change_list_template = "admin/vocabulary_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
            path('export-csv/', self.export_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            created = updated = errors = 0
            error_messages = []

            with transaction.atomic():
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Create Arabic entry
                        ar_obj, ar_created = Vocabulary.objects.update_or_create(
                            concept=row['concept'],
                            language='ar',
                            defaults={
                                'text': row['arabic_word__text'],
                                'hint': row['hint'],
                                'is_correct': True
                            }
                        )

                        # Create Hebrew entry with validation
                        he_obj, he_created = Vocabulary.objects.update_or_create(
                            concept=row['concept'],
                            language='he',
                            defaults={
                                'text': row['hebrew_word__text'],
                                'hint': row['hint'],
                                'is_correct': True
                            }
                        )
                        he_obj.full_clean()  # Explicit validation

                        # Create English entry
                        en_obj, en_created = Vocabulary.objects.update_or_create(
                            concept=row['concept'],
                            language='en',
                            defaults={
                                'text': row['concept'],
                                'hint': row['hint'],
                                'is_correct': False
                            }
                        )

                        if ar_created:
                            created += 1
                        else:
                            updated += 1
                        if he_created:
                            created += 1
                        else:
                            updated += 1
                        if en_created:
                            created += 1
                        else:
                            updated += 1

                    except ValidationError as e:
                        errors += 1
                        error_messages.append(
                            f"Row {row_num} ({row['concept']}): {', '.join(e.messages)}"
                        )
                    except Exception as e:
                        errors += 1
                        error_messages.append(
                            f"Row {row_num} ({row['concept']}): {str(e)}"
                        )

            if errors:
                self.message_user(
                    request,
                    f"Completed with {errors} errors. Imported {created} new and updated {updated} existing entries",
                    level='ERROR'
                )
                for msg in error_messages[:10]:  # Show first 10 errors
                    self.message_user(request, msg, level='ERROR')
            else:
                self.message_user(
                    request,
                    f"Successfully imported {created} new and updated {updated} existing entries"
                )

            return redirect("..")

        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )

    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vocabulary_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['concept', 'hint', 'arabic_word__text', 'hebrew_word__text'])

        for entry in VocabularyEntry.objects.all():
            writer.writerow([
                entry.concept,
                entry.hint,
                entry.arabic_text,
                entry.hebrew_text
            ])

        return response

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('text', 'language', 'is_correct', 'styled_preview')
    list_filter = ('language', 'is_correct')
    search_fields = ('text',)
    list_editable = ('is_correct',)

    def styled_preview(self, obj):
        if obj.language == 'he':
            return format_html('<span style="direction: rtl; font-family: David, Arial; font-size: 16px;">{}</span>',
                               obj.text)
        elif obj.language == 'ar':
            return format_html('<span style="font-family: Traditional Arabic, Arial; font-size: 16px;">{}</span>',
                               obj.text)
        return obj.text

    styled_preview.short_description = "Styled Display"


class GameResponseInline(admin.TabularInline):
    model = GameResponse
    extra = 0
    readonly_fields = ('concept', 'selected_text', 'is_correct', 'response_time_ms', 'submitted_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'created_at', 'language_preference', 'response_count')
    list_filter = ('language_preference', 'created_at')
    search_fields = ('session_id', 'device_id')
    inlines = [GameResponseInline]

    def response_count(self, obj):
        return obj.responses.count()

    response_count.short_description = "Answers"


@admin.register(GameResponse)
class GameResponseAdmin(admin.ModelAdmin):
    list_display = ('session', 'entry_display', 'selected_word_display', 'is_correct', 'response_time')
    list_filter = ('is_correct', 'submitted_at')
    readonly_fields = ('submitted_at',)

    def entry_display(self, obj):
        return obj.entry.arabic_text

    entry_display.short_description = "Arabic Word"

    def selected_word_display(self, obj):
        lang = obj.selected_word.get_language_display()
        return f"[{lang}] {obj.selected_word.text}"

    selected_word_display.short_description = "Selected Answer"

    def response_time(self, obj):
        return f"{obj.response_time_ms}ms"

    response_time.short_description = "Time"


admin.site.site_header = "Vocabulary Learning Admin"
admin.site.site_title = "Vocabulary System"
admin.site.index_title = "Welcome to Vocabulary Admin"