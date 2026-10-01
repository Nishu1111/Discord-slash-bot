from django.db import models


class CommandLog(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received"
        PROCESSED = "processed"
        FAILED = "failed"

    interaction_id = models.CharField(
        max_length=32,
        unique=True,
    )

    interaction_type = models.PositiveSmallIntegerField()

    command_name = models.CharField(
        max_length=64,
        blank=True,
    )

    options = models.JSONField(
        default=dict,
        blank=True,
    )

    guild_id = models.CharField(
        max_length=32,
        blank=True,
        db_index=True,
    )

    channel_id = models.CharField(
        max_length=32,
        blank=True,
    )

    user_id = models.CharField(
        max_length=32,
        blank=True,
    )

    username = models.CharField(
        max_length=100,
        blank=True,
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.RECEIVED,
    )

    response_payload = models.JSONField(
        null=True,
        blank=True,
    )

    error = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.command_name} ({self.interaction_id})"