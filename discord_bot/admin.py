from django.contrib import admin
from .models import CommandLog


@admin.register(CommandLog)
class CommandLogAdmin(admin.ModelAdmin):
    list_display = (
        "interaction_id",
        "command_name",
        "username",
        "status",
        "created_at",
        "processed_at",
    )

    list_filter = (
        "status",
        "command_name",
    )

    search_fields = (
        "interaction_id",
        "username",
        "command_name",
        "guild_id",
    )