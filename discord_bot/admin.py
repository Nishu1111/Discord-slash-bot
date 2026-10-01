from django.contrib import admin
from .models import CommandLog, MirrorAttempt


@admin.register(CommandLog)
class CommandLogAdmin(admin.ModelAdmin):
    list_display = (
        "interaction_id",
        "command_name",
        "username",
        "status",
        "created_at",
        "processed_at",
        "action",
        "mirror_status",
        "mirror_attempts",
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
    
@admin.register(MirrorAttempt)
class MirrorAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "log",
        "attempt_no",
        "ok",
        "http_status",
        "error",
        "created_at",
    )