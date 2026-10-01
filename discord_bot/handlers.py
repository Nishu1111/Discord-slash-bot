from .models import CommandRule
#manual words 
# URGENT_WORDS = (
#     "urgent",
#     "down",
#     "outage",
#     "critical",
#     "failing",
# )

DEFAULT = ("logged", True)

def classify(command_name, text):
    text = text.lower()

    for rule in CommandRule.objects.filter(
        enabled=True,
        command_name=command_name,
    ):
        if any(keyword in text for keyword in rule.keyword_list()):
            return rule.action, rule.mirror

    return DEFAULT
    
def handle_status(interaction):
    return {
        "type": 4,
        "data": {
            "content": "Bot is online and healthy."
        },
    }


def handle_report(interaction):
    return {
        "type": 5,
    }


HANDLERS = {
    "status": handle_status,
    "report": handle_report,
}