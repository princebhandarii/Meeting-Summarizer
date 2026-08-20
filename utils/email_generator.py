from utils.groq_client import ask_groq


def generate_followup_email(summary, decisions, action_items, model=None):
    decisions_text = "\n".join(f"- {d}" for d in decisions) if decisions else "None recorded."

    if action_items:
        action_items_text = "\n".join(
            f"- {item.get('task', 'N/A')} "
            f"(Assignee: {item.get('assignee', 'Unassigned')}, "
            f"Deadline: {item.get('deadline', 'Not specified')}, "
            f"Priority: {item.get('priority', 'N/A')})"
            for item in action_items
        )
    else:
        action_items_text = "None recorded."

    prompt = f"""Write a professional follow-up email to send to meeting attendees.

Meeting Summary:
{summary}

Key Decisions:
{decisions_text}

Action Items:
{action_items_text}

Keep it professional. Start with a brief thank-you/recap, include a Key Decisions section
and an Action Items section (with assignee and deadline), and end with a polite closing.
Don't include a subject line placeholder, just the email body.
"""
    return ask_groq(prompt, temperature=0.4, max_tokens=600, model=model)
