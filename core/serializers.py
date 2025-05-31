from rest_framework import serializers
from .models import VocabularyEntry, Word, Player, Score

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'text']

class QuizSerializer(serializers.Serializer):
    question_word = serializers.CharField()
    question_language = serializers.CharField()
    options = WordSerializer(many=True)
    gif = serializers.FileField(required=False)

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name']

class ScoreSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all())

    class Meta:
        model = Score
        fields = ['id', 'player', 'value', 'created_at']
        read_only_fields = ['created_at']