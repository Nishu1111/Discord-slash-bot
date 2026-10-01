from django.urls import path
from .views import health, discord_interactions


urlpatterns = [
    path("", health),
    path("health/", health),
    path("discord/interaction/", discord_interactions)
]