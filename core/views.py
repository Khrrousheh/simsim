import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VocabularyEntry, Word, PlayerScore
from .serializers import QuizSerializer, WordSerializer, PlayerScoreSerializer

@api_view(['GET'])
def get_quiz_question(request):
    entries = VocabularyEntry.objects.prefetch_related('words').all()

    if not entries.exists():
        return Response({'detail': 'No vocabulary entries found'}, status=404)

    entry = random.choice(entries)

    words = list(entry.words.all())
    if len(words) != 2:
        return Response({'detail': 'Each entry must have one Arabic and one Hebrew word'}, status=400)

    arabic_word = next((w for w in words if w.language == 'ar'), None)
    hebrew_word = next((w for w in words if w.language == 'he'), None)

    if not arabic_word or not hebrew_word:
        return Response({'detail': 'Missing Arabic or Hebrew word'}, status=400)

    is_question_in_arabic = random.choice([True, False])
    question_word = arabic_word.text if is_question_in_arabic else hebrew_word.text
    question_lang = 'ar' if is_question_in_arabic else 'he'
    answer_lang = 'he' if is_question_in_arabic else 'ar'
    correct_answer = hebrew_word if is_question_in_arabic else arabic_word

    # Get 3 random distractors from other entries
    distractors = Word.objects.filter(language=answer_lang).exclude(id=correct_answer.id)
    options = random.sample(list(distractors), min(3, distractors.count()))
    options.append(correct_answer)
    random.shuffle(options)

    response_data = {
        'question_word': question_word,
        'question_language': question_lang,
        'options': WordSerializer(options, many=True).data,
        'gif': request.build_absolute_uri(entry.gif.url) if entry.gif else None
    }

    return Response(response_data)

@api_view(['GET'])
def player_scores_list(request):
    scores = PlayerScore.objects.all()
    serializer = PlayerScoreSerializer(scores, many=True)
    return Response(serializer.data)