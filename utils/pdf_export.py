from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def build_pdf_report(title, summary, decisions, topics, action_items, transcript):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(escape(title), styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(Paragraph(escape(summary or "N/A"), styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Key Decisions", styles["Heading2"]))
    if decisions:
        for d in decisions:
            story.append(Paragraph(f"- {escape(d)}", styles["BodyText"]))
    else:
        story.append(Paragraph("None recorded.", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Topics Discussed", styles["Heading2"]))
    if topics:
        for t in topics:
            line = f"<b>{escape(t.get('title', 'Untitled'))}</b>: {escape(t.get('summary', ''))}"
            story.append(Paragraph(line, styles["BodyText"]))
    else:
        story.append(Paragraph("None recorded.", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Action Items", styles["Heading2"]))
    if action_items:
        for item in action_items:
            line = (
                f"- {escape(item.get('task', 'N/A'))} "
                f"(Assignee: {escape(item.get('assignee', 'Unassigned'))}, "
                f"Deadline: {escape(item.get('deadline', 'Not specified'))}, "
                f"Priority: {escape(item.get('priority', 'N/A'))})"
            )
            story.append(Paragraph(line, styles["BodyText"]))
    else:
        story.append(Paragraph("None recorded.", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Full Transcript", styles["Heading2"]))
    transcript_html = escape(transcript or "").replace("\n", "<br/>")
    story.append(Paragraph(transcript_html, styles["BodyText"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
