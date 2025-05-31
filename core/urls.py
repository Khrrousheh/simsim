from django.urls import path
from .views import get_quiz_question

urlpatterns = [
    path('quiz/', get_quiz_question, name='quiz-question'),
]
