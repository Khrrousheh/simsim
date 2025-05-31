from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .models import Vocabulary, GameSession, GameResponse
import random


@api_view(['GET'])
def get_game_vocabulary(request):
    language = request.GET.get('language', 'he')
    count = int(request.GET.get('count', 10))

    # Get random Arabic concepts
    concepts = list(Vocabulary.objects.filter(language='ar')
                    .order_by('?')[:count].values_list('concept', flat=True))

    questions = []
    for concept in concepts:
        # Get correct translation
        correct = Vocabulary.objects.get(concept=concept, language=language, is_correct=True)

        # Get 3 incorrect options (same language)
        incorrect = list(Vocabulary.objects.filter(language=language, is_correct=False)
                         .exclude(text=correct.text).order_by('?')[:3])

        options = [correct] + incorrect
        random.shuffle(options)

        # Get Arabic text for question
        arabic = Vocabulary.objects.get(concept=concept, language='ar')

        questions.append({
            'concept': concept,
            'question': arabic.text,
            'options': [{
                'id': opt.id,
                'text': opt.text,
                'is_correct': opt.is_correct
            } for opt in options],
            'hint': arabic.hint
        })

    # Create or get session
    session_id = request.GET.get('session_id')
    if not session_id:
        session = GameSession.objects.create(
            session_id=generate_session_id(),
            language_preference=language
        )
        session_id = session.session_id
    else:
        session = GameSession.objects.get(session_id=session_id)

    return Response({
        'session_id': session_id,
        'questions': questions
    })


@api_view(['POST'])
def submit_game_responses(request):
    data = request.data
    try:
        session = GameSession.objects.get(session_id=data['session_id'])

        for response in data['responses']:
            # Get the correct answer to validate length consistency
            correct_answer = Vocabulary.objects.get(
                concept=response['concept'],
                language='he',
                is_correct=True
            )
            arabic_entry = Vocabulary.objects.get(
                concept=response['concept'],
                language='ar',
                is_correct=True
            )

            # This validation would have been done during import, but double-check
            if len(correct_answer.text.strip()) != len(arabic_entry.text.strip()):
                return Response(
                    {'error': f"Length mismatch for concept {response['concept']}"},
                    status=400
                )

            GameResponse.objects.create(
                session=session,
                concept=response['concept'],
                selected_text=response['selected_text'],
                is_correct=response['is_correct'],
                response_time_ms=response['response_time_ms']
            )

        return Response({'status': 'success'})

    except Exception as e:
        return Response({'error': str(e)}, status=400)


def generate_session_id():
    # Implement your session ID generation logic
    import uuid
    return str(uuid.uuid4())