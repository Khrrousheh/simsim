from rest_framework import serializers
from .models import VocabularyEntry, Word, PlayerScore

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'text']

class QuizSerializer(serializers.Serializer):
    question_word = serializers.CharField()
    question_language = serializers.CharField()
    options = WordSerializer(many=True)
    gif = serializers.FileField(required=False)

class PlayerScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerScore
        fields = ['name', 'score']
