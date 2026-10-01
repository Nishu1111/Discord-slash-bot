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
    
    class MirrorStatus(models.TextChoices):
        NOT_APPLICABLE = "not_applicable"
        PENDING = "pending"
        SENT = "sent"
        FAILED = "failed"

    #store the simple rule
    action = models.CharField(max_length=32, blank=True)          # flagged_urgent / logged
    
    #track the current mirror status
    mirror_status = models.CharField(
        max_length=16, 
        choices=MirrorStatus.choices,
        default=MirrorStatus.NOT_APPLICABLE)
    
    # count tried times
    mirror_attempts = models.PositiveSmallIntegerField(default=0)
    
    #latest failer reason
    mirror_last_error = models.CharField(max_length=200, blank=True)
    
class MirrorAttempt(models.Model):
    log = models.ForeignKey(
        CommandLog,
        on_delete=models.CASCADE,
        related_name="attempts",
    )

    attempt_no = models.PositiveSmallIntegerField()

    ok = models.BooleanField()

    http_status = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    error = models.CharField(
        max_length=200,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]