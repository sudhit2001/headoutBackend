from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.register),
    path('login',views.login),
    path("next_question", views.next_question),  # 🔹 Fetch Next Question
    path("submit_answer", views.submit_answer),
    path("challenge_friend", views.challenge_friend),
    path("check_token", views.check),
]
