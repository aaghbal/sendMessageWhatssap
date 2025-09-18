from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_overview, name='analytics_overview'),
    path('campaigns/<int:campaign_id>/', views.campaign_analytics_detail, name='campaign_analytics_detail'),
]
