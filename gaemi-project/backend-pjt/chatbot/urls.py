# chatbot/urls.py
from django.urls import path
from .views import ChatbotRAGView

urlpatterns = [
    path('ask/', ChatbotRAGView.as_view(), name='ask_chatbot'),
]