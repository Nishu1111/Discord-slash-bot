from django.urls import path
from .views import health, discord_interactions


urlpatterns = [
    path("health/", health),
    path("discord/interaactions/", discord_interactions)
]