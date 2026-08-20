import uuid
from datetime import datetime, timedelta
from dateutil import parser as date_parser


def _try_parse_date(text):
    if not text or text.strip().lower() in ("not specified", "n/a", "none", "unspecified", ""):
        return None
    try:
        return date_parser.parse(text, fuzzy=True, default=datetime.now())
    except (ValueError, OverflowError):
        return None


def build_ics(action_items):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Meeting Summarizer//EN"]

    for item in action_items:
        due = _try_parse_date(item.get("deadline", ""))
        if due is None:
            continue

        end = due + timedelta(hours=1)
        uid = str(uuid.uuid4())
        summary = item.get("task", "Action item")
        description = f"Assignee: {item.get('assignee', 'Unassigned')}, Priority: {item.get('priority', 'N/A')}"

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{due.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return "\n".join(lines)
