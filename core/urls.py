from django.urls import path
from .views import get_quiz_question, player_scores_list, player_create, score_create

urlpatterns = [
    path('quiz/', get_quiz_question, name='quiz-question'),
    # path('scores/', player_scores_list, name='player_scores_list'),
    path('players/', player_create, name='player-create'),
    path('scores/', score_create, name='score-create'),

]
