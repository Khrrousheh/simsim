from rest_framework import serializers
from .models import VocabularyEntry, Word

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'text']

class QuizSerializer(serializers.Serializer):
    question_word = serializers.CharField()
    question_language = serializers.CharField()
    options = WordSerializer(many=True)
    gif = serializers.FileField(required=False)
