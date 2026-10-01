# Django authentication and permission helpers
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

# Pagination and database query helpers
from django.core.paginator import Paginator
from django.db.models import Count, Q

# Common Django shortcuts
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

# Restrict a view to POST requests
from django.views.decorators.http import require_POST

# Generic class-based views
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

# Our mirror function and retry limit
from .mirror import send_mirror, MAX_ATTEMPTS

# Our database models
from .models import CommandLog, CommandRule


# Only active staff users can access the dashboard
admin_required = user_passes_test(
    lambda u: u.is_active and u.is_staff,
    login_url="/login/",
)


# Dashboard showing command logs and statistics
@admin_required
def dashboard(request):
    # Start with all logs, newest first
    qs = CommandLog.objects.all().order_by("-created_at")

    # Read filters from the URL
    status = request.GET.get("status", "")
    command = request.GET.get("command", "")
    mirror = request.GET.get("mirror", "")
    q = request.GET.get("q", "").strip()

    # Filter by command status
    if status:
        qs = qs.filter(status=status)

    # Filter by command name
    if command:
        qs = qs.filter(command_name=command)

    # Filter by mirror status
    if mirror:
        qs = qs.filter(mirror_status=mirror)

    # Search username, interaction ID, or report text
    if q:
        qs = qs.filter(
            Q(username__icontains=q)
            | Q(interaction_id__icontains=q)
            | Q(options__text__icontains=q)
        )

    # Show 25 logs per page
    page = Paginator(qs, 25).get_page(
        request.GET.get("page")
    )

    # Use a smaller template when only table rows are requested
    template = (
        "dashboard/rows.html"
        if request.GET.get("partial")
        else "dashboard/index.html"
    )

    # Data sent to the dashboard template
    #ctx is context
    ctx = {
        "page": page,

        # Current filter values
        "filters": {
            "status": status,
            "command": command,
            "mirror": mirror,
            "q": q,
        },

        # Dashboard statistics
        "stats": CommandLog.objects.aggregate(
            # Total number of logs.
            total=Count("id"),

            # Number of failed commands
            failed=Count(
                "id",
                filter=Q(status="failed"),
            ),

            # Number of failed mirror attempts
            mirror_failed=Count(
                "id",
                filter=Q(mirror_status="failed"),
            ),

            # Number of mirrors waiting to be sent
            mirror_pending=Count(
                "id",
                filter=Q(mirror_status="pending"),
            ),
        ),

        # Get the different command names used in the logs
        "commands": (
            CommandLog.objects
            .values_list("command_name", flat=True)
            .distinct()
        ),

        # Status choices used by the dashboard filter
        # Django templates cannot use "string".split
        "status_choices": [
            "received",
            "processed",
            "failed",
        ],

        # Mirror status choices used by the dashboard filter
        "mirror_choices": [
            "pending",
            "sent",
            "failed",
            "not_applicable",
        ],
    }

    # Render the selected dashboard template
    return render(request, template, ctx)


# Show details for one command log.
@admin_required
def log_detail(request, pk):
    # Find the log or return a 404 page if it doesn't exist
    log = get_object_or_404(
        CommandLog,
        pk=pk,
    )

    # Show the log and its mirror attempts
    return render(
        request,
        "dashboard/detail.html",
        {
            "log": log,
            "attempts": log.attempts.all(),
            "max_attempts": MAX_ATTEMPTS,
        },
    )


# Manually retry a failed mirror
@admin_required
@require_POST
def retry_one(request, pk):
    # Find the log or return 404
    log = get_object_or_404(
        CommandLog,
        pk=pk,
    )

    # Only retry if the previous mirror failed
    if log.mirror_status == CommandLog.MirrorStatus.FAILED:
        send_mirror(log)

    # Return to the log details page
    return redirect(
        "log_detail",
        pk=pk,
    )


# Reusable permission check for class-based views
class StaffMixin(UserPassesTestMixin):
    login_url = "/login/"

    def test_func(self):
        user = self.request.user

        # User must be logged in, active, and staff
        return (
            user.is_authenticated
            and user.is_active
            and user.is_staff
        )


# Display all command rules
class RuleList(StaffMixin, ListView):
    model = CommandRule
    template_name = "dashboard/rules.html"


# Create a new command rule
class RuleCreate(StaffMixin, CreateView):
    model = CommandRule

    # Fields that staff can enter in the rule form
    fields = [
        "name",
        "command_name",
        "keywords",
        "action",
        "mirror",
        "priority",
        "enabled",
    ]

    template_name = "dashboard/rule_form.html"

    # Where to go after successfully creating a rule
    success_url = reverse_lazy("rules")


# Edit an existing command rule
class RuleUpdate(RuleCreate, UpdateView):
    pass


# Delete an existing command rule
class RuleDelete(StaffMixin, DeleteView):
    model = CommandRule
    template_name = "dashboard/rule_confirm_delete.html"

    # Where to go after deleting the rule
    success_url = reverse_lazy("rules")