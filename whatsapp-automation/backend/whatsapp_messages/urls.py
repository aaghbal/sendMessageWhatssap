from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.MessageTemplateViewSet, basename='message-templates')
router.register(r'sent', views.SentMessageViewSet, basename='sent-messages')

urlpatterns = [
    path('', include(router.urls)),
]
