from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .models import VocabularyEntry, GameSession, GameResponse
import random
from rest_framework.views import APIView
from rest_framework import status


def generate_session_id():
    """Generate a unique session ID using UUID"""
    import uuid
    return str(uuid.uuid4())


class GameVocabularyView(APIView):
    """
    API endpoint to get vocabulary questions for the game
    """

    def get(self, request):
        try:
            # Get parameters with defaults
            lang = request.GET.get('LANG', 'he')  # Default to Hebrew
            try:
                n = int(request.GET.get('N', 5))  # Default to 5 questions
            except ValueError:
                return Response(
                    {'error': 'N must be an integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate language
            if lang not in ['ar', 'he']:
                return Response(
                    {'error': 'Language must be either "ar" (Arabic) or "he" (Hebrew)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get random vocabulary entries
            entries = list(VocabularyEntry.objects.all())
            if len(entries) < n:
                return Response(
                    {'error': f'Not enough vocabulary available (need {n}, have {len(entries)})'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            selected_entries = random.sample(entries, n)
            questions = self._prepare_questions(selected_entries, lang)

            # Handle session
            session_id = request.GET.get('session_id')
            session = self._get_or_create_session(session_id, lang)

            return Response({
                'session_id': session.session_id,
                'questions': questions
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _prepare_questions(self, entries, lang):
        """Prepare question data for the response"""
        questions = []
        for entry in entries:
            # Get question text in the requested language
            question_text = entry.hebrew_text if lang == 'he' else entry.arabic_text

            # Get correct answer in opposite language
            correct_answer_text = entry.arabic_text if lang == 'he' else entry.hebrew_text

            # Get all possible answers in opposite language
            answer_lang = 'he' if lang == 'ar' else 'ar'
            all_entries = VocabularyEntry.objects.exclude(id=entry.id)
            other_answers = [
                e.arabic_text if answer_lang == 'ar' else e.hebrew_text
                for e in all_entries
            ]

            # Select 3 incorrect options
            incorrect = random.sample(other_answers, min(3, len(other_answers)))

            # Combine correct and incorrect answers
            correct_answer = {
                'id': f'correct_{entry.id}',
                'text': correct_answer_text
            }
            options = [correct_answer] + [
                {'id': f'incorrect_{i}', 'text': text} for i, text in enumerate(incorrect)
            ]
            random.shuffle(options)

            questions.append({
                'question': question_text,
                'options': options,
                'answer': correct_answer['id'],
                'concept': entry.concept  # Add concept for response submission
            })

        return questions

    def _get_or_create_session(self, session_id, lang):
        """Get existing session or create a new one"""
        if session_id:
            try:
                return GameSession.objects.get(session_id=session_id)
            except GameSession.DoesNotExist:
                pass

        return GameSession.objects.create(
            session_id=generate_session_id(),
            language_preference=lang
        )


class SubmitGameView(APIView):
    """
    API endpoint to submit game responses
    """

    def post(self, request):
        data = request.data
        try:
            # Validate required fields
            if 'session_id' not in data:
                return Response(
                    {'error': 'session_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'responses' not in data or not isinstance(data['responses'], list):
                return Response(
                    {'error': 'responses must be a list'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            session = GameSession.objects.get(session_id=data['session_id'])
            self._save_responses(session, data['responses'])

            return Response({'status': 'success'})

        except GameSession.DoesNotExist:
            return Response(
                {'error': 'Invalid session ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except KeyError as e:
            return Response(
                {'error': f'Missing required field: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _save_responses(self, session, responses):
        """Save all game responses to the database"""
        for response in responses:
            # Validate each response has required fields
            required_fields = ['concept', 'selected_text', 'is_correct', 'response_time_ms']
            if not all(field in response for field in required_fields):
                raise KeyError(f"Response missing one of {required_fields}")

            GameResponse.objects.create(
                session=session,
                concept=response['concept'],
                selected_text=response['selected_text'],
                is_correct=response['is_correct'],
                response_time_ms=response['response_time_ms']
            )


# Legacy function-based views (keep for backward compatibility if needed)
@api_view(['GET'])
def get_game_vocabulary(request):
    """Legacy function-based view (redirects to class-based view)"""
    view = GameVocabularyView()
    return view.get(request)


@api_view(['POST'])
def submit_game_responses(request):
    """Legacy function-based view (redirects to class-based view)"""
    view = SubmitGameView()
    return view.post(request)