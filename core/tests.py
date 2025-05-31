from django.test import TestCase
from core.models import VocabularyEntry, Word
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from .models import VocabularyEntry, Word

# model validation test
class WordValidationTest(TestCase):
    def test_hebrew_and_arabic_same_length(self):
        entry = VocabularyEntry.objects.create(arabic_text="مرحبا")
        
        # Hebrew translation with same length
        correct_word = Word(entry=entry, text="שלום", is_correct=True)
        with self.assertRaises(ValidationError):
            correct_word.full_clean()


class QuizAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create multiple entries
        for i in range(5):
            entry = VocabularyEntry.objects.create(arabic_text=f"كلمة{i}")
            Word.objects.create(text=f"hebrew{i}", language='he', entry=entry)
            Word.objects.create(text=f"arabic{i}", language='ar', entry=entry)

    def test_quiz_api_returns_question(self):
        response = self.client.get(reverse('quiz-question'))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('question_word', data)
        self.assertIn('question_language', data)
        self.assertIn('options', data)

        self.assertIsInstance(data['options'], list)
        self.assertEqual(len(data['options']), 4)

    def test_quiz_question_language_is_valid(self):
        response = self.client.get(reverse('quiz-question'))
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn(data['question_language'], ['ar', 'he'])

    def test_quiz_includes_gif_if_present(self):
        entry = VocabularyEntry.objects.create(arabic_text="كلمة6", gif="gifs/example.gif")
        Word.objects.create(text="hebrew6", language="he", entry=entry)
        Word.objects.create(text="arabic6", language="ar", entry=entry)

        response = self.client.get(reverse('quiz-question'))
        self.assertEqual(response.status_code, 200)

        # GIF is optional, so we just verify field exists
        self.assertIn('gif', response.json())