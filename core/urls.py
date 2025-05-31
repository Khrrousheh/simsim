from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import get_game_vocabulary, submit_game_responses

urlpatterns = [
    # Game logic endpoints
    path('game/vocabulary/', get_game_vocabulary, name='game-vocabulary'),
    path('game/submit/', submit_game_responses, name='submit-game-responses'),

    # JWT authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
