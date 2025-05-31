from rest_framework import serializers
from .models import VocabularyEntry, Vocabulary, GameSession, GameResponse


class VocabularyEntrySerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = VocabularyEntry
        fields = ['id', 'concept', 'hint', 'arabic_text', 'hebrew_text', 'image', 'created_at']
        read_only_fields = ('created_at',)


class VocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vocabulary
        fields = ['id', 'concept', 'language', 'text', 'hint', 'is_correct']
        # The 'language' field has choices defined in the model.
        # The model also has a unique_together constraint on ('concept', 'language').
        # DRF automatically handles these.

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['id', 'session_id', 'created_at', 'language_preference']
        read_only_fields = ('created_at',) # 'created_at' is auto_now_add

class GameResponseSerializer(serializers.ModelSerializer):
    # By default, the 'session' ForeignKey will be represented by its primary key.
    # You can customize this using PrimaryKeyRelatedField, StringRelatedField,
    # or a nested serializer (e.g., GameSessionSerializer(read_only=True))
    # if you want to display more session details.
    # For example:
    # session = GameSessionSerializer(read_only=True) # For nested read-only representation
    # session = serializers.PrimaryKeyRelatedField(queryset=GameSession.objects.all()) # Explicitly for write

    class Meta:
        model = GameResponse
        fields = ['id', 'session', 'concept', 'selected_text', 'is_correct', 'response_time_ms', 'submitted_at']
        read_only_fields = ('submitted_at',) # 'submitted_at' is auto_now_add