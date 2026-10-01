import os

import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Register Discord slash commands"

    def handle(self, *args, **options):
        application_id = os.getenv("DISCORD_APP_ID")
        bot_token = os.getenv("DISCORD_BOT_TOKEN")

        if not application_id:
            self.stdout.write(
                self.style.ERROR("DISCORD_APP_ID is missing")
            )
            return

        if not bot_token:
            self.stdout.write(
                self.style.ERROR("DISCORD_BOT_TOKEN is missing")
            )
            return

        url = (
            f"https://discord.com/api/v10/"
            f"applications/{application_id}/commands"
        )

        commands = [
            {
                "name": "status",
                "description": "Check the bot status",
            },
            {
                "name": "report",
                "description": "Submit a report",
                "options": [
                    {
                        "name": "text",
                        "description": "The report text",
                        "type": 3,
                        "required": True,
                    }
                ],
            },
        ]

        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        }

        for command in commands:
            response = requests.post(
                url,
                json=command,
                headers=headers,
                timeout=10,
            )

            if response.status_code in (200, 201):
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Registered /{command['name']}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to register /{command['name']}: "
                        f"{response.status_code} {response.text}"
                    )
                )