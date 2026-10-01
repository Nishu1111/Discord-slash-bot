
#manual words 
URGENT_WORDS = (
    "urgent",
    "down",
    "outage",
    "critical",
    "failing",
)


def classify(text):
    t = text.lower()

    return (
        "flagged_urgent"
        if any(word in t for word in URGENT_WORDS)
        else "logged"
    )
    
def handle_status(interaction):
    return {
        "type": 4,
        "data": {
            "content": "Bot is online and healthy."
        },
    }


def handle_report(interaction):
    text = next(
        (
            option["value"]
            for option in interaction.get("data", {}).get("options", [])
            if option["name"] == "text"
        ),
        "",
    )

    return {
        "type": 4,
        "data": {
            "content": f"Report received: {text}"
        },
    }


HANDLERS = {
    "status": handle_status,
    "report": handle_report,
}