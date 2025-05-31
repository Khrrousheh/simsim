from django.urls import path
from . import views

urlpatterns = [
    path('api/game/vocabulary/', views.GameVocabularyView.as_view(), name='game-vocabulary'),
    path('api/game/submit/', views.SubmitGameView.as_view(), name='submit-game'),
]