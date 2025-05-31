from django.urls import path
from .views import get_quiz_question, player_scores_list

urlpatterns = [
    path('quiz/', get_quiz_question, name='quiz-question'),
    path('scores/', player_scores_list, name='player_scores_list'),
]
