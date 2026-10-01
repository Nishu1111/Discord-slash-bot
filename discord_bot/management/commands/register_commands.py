import os
import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Register Discord slash commands"

    def handle(self, *args, **options):
        # Get Discord App ID and Bot Token from environment variables
        application_id = os.getenv("DISCORD_APP_ID")
        bot_token = os.getenv("DISCORD_BOT_TOKEN")

        # Check if App ID is available
        if not application_id:
            self.stdout.write(
                self.style.ERROR("DISCORD_APP_ID is missing")
            )
            return

        # Check if Bot Token is available
        if not bot_token:
            self.stdout.write(
                self.style.ERROR("DISCORD_BOT_TOKEN is missing")
            )
            return

        # Discord API URL used to register slash commands
        url = (
            f"https://discord.com/api/v10/"
            f"applications/{application_id}/commands"
        )

        # Define the slash commands we want to create
        commands = [
            {
                # Creates /status command
                "name": "status",
                "description": "Check the bot status",
            },
            {
                # Creates /report command
                "name": "report",
                "description": "Submit a report",

                # /report requires a text input
                "options": [
                    {
                        "name": "text",
                        "description": "The report text",

                        # Type 3 means STRING in Discord
                        "type": 3,
                        "required": True,
                    }
                ],
            },
        ]

        # Headers required for Discord API authentication
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        }

        # Register each command with Discord
        for command in commands:
            response = requests.post(
                url,
                json=command,
                headers=headers,
                timeout=10,
            )

            # Discord returns 200 or 201 when registration succeeds
            if response.status_code in (200, 201):
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Registered /{command['name']}"
                    )
                )
            else:
                # Show error details if registration fails
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to register /{command['name']}: "
                        f"{response.status_code} {response.text}"
                    )
                )