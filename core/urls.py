from django.urls import path
from .views import get_game_vocabulary, submit_game_responses

urlpatterns = [
    # Game logic endpoints
    path('game/vocabulary/', get_game_vocabulary, name='game-vocabulary'),
    path('game/submit/', submit_game_responses, name='submit-game-responses'),
]
