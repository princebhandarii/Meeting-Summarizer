import html

import streamlit as st
from dotenv import load_dotenv

from utils.audio_handler import save_temp_audio, cleanup_temp_audio
from utils.audio_player import build_player_html, guess_mime
from utils.transcriber import transcribe_audio
from utils.summarizer import generate_summary
from utils.action_items import extract_action_items
from utils.topics_decisions import extract_topics_and_decisions
from utils.qna import answer_question
from utils.email_generator import generate_followup_email
from utils.meeting_title import generate_meeting_title
from utils.calendar_export import build_ics
from utils.pdf_export import build_pdf_report
from utils.groq_client import AVAILABLE_LLM_MODELS

load_dotenv()

st.set_page_config(page_title="Meeting Summarizer", layout="wide")

APP_CSS = """
<style>
.stApp { background-color: #0E1117; }
.stApp, [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
h1, h2, h3, h4, label, [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stCaptionContainer"], .segment-row {
    color: #FAFAFA !important;
}
[data-testid="stSidebar"] { background-color: #1C1F26; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

WHISPER_MODELS = ["tiny", "base", "small"]
LANGUAGE_MODES = ["Auto-detect", "Translate to English"]

defaults = {
    "transcript": None,
    "segments": None,
    "detected_language": None,
    "duration_seconds": None,
    "summary": None,
    "action_items": None,
    "topics_decisions": None,
    "qna_history": [],
    "meeting_title": None,
    "audio_bytes": None,
    "audio_mime": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.title("Meeting Summarizer")
st.caption(
    "Upload a meeting recording to get a transcript, AI summary, action items, "
    "topic breakdown, Q and A, and a ready to send follow up email."
)

left_col, right_col = st.columns([1, 1.3])

with left_col:
    st.subheader("Upload and Settings")

    uploaded_file = st.file_uploader("Upload meeting audio", type=["mp3", "wav", "m4a"])
    if uploaded_file is not None:
        st.audio(uploaded_file)

    context = st.text_area(
        "Context (optional)",
        placeholder="For example: Weekly product marketing sync with the growth team",
        height=80,
    )

    language_mode = st.selectbox("Language handling", LANGUAGE_MODES, index=0)

    whisper_model = st.selectbox(
        "Whisper model for speech to text",
        WHISPER_MODELS,
        index=WHISPER_MODELS.index("base"),
        help="Bigger models are more accurate but slower and use more RAM.",
    )

    llm_model = st.selectbox(
        "Model for summarization and analysis",
        AVAILABLE_LLM_MODELS,
        index=0,
        help="gpt-oss-20b is faster, gpt-oss-120b is more capable.",
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        clear_clicked = st.button("Clear", use_container_width=True)
    with btn_col2:
        submit_clicked = st.button("Submit", type="primary", use_container_width=True)

    if clear_clicked:
        for key, value in defaults.items():
            st.session_state[key] = value
        st.session_state.pop("email_text", None)
        st.rerun()

    if submit_clicked:
        if uploaded_file is None:
            st.warning("Please upload an audio file first.")
        else:
            temp_path = None
            try:
                audio_bytes = uploaded_file.getvalue()
                st.session_state.audio_bytes = audio_bytes
                st.session_state.audio_mime = guess_mime(uploaded_file.name)

                with st.spinner("Transcribing audio..."):
                    temp_path = save_temp_audio(audio_bytes, uploaded_file.name)
                    result = transcribe_audio(
                        temp_path,
                        model_size=whisper_model,
                        translate=(language_mode == "Translate to English"),
                    )
                    transcript_text = result["text"]
                    segments = result["segments"]
                    st.session_state.detected_language = result["language"]
                    st.session_state.duration_seconds = result["duration"]

                if not transcript_text.strip():
                    st.warning("No speech was detected in this audio file.")
                else:
                    st.session_state.transcript = transcript_text
                    st.session_state.segments = segments

                    with st.spinner("Generating summary..."):
                        st.session_state.summary = generate_summary(
                            transcript_text, context=context, model=llm_model
                        )
                    with st.spinner("Extracting action items..."):
                        st.session_state.action_items = extract_action_items(
                            transcript_text, context=context, model=llm_model
                        )
                    with st.spinner("Detecting topics and decisions..."):
                        st.session_state.topics_decisions = extract_topics_and_decisions(
                            transcript_text, context=context, model=llm_model
                        )
                    with st.spinner("Naming the meeting..."):
                        st.session_state.meeting_title = generate_meeting_title(
                            transcript_text[:2000], context=context, model=llm_model
                        )

                    st.session_state.qna_history = []
                    st.session_state.llm_model = llm_model
                    st.success("Meeting analyzed successfully.")

            except Exception as e:
                st.error(f"Something went wrong while processing this file: {e}")
            finally:
                if temp_path:
                    cleanup_temp_audio(temp_path)

with right_col:
    if st.session_state.transcript:
        transcript = st.session_state.transcript
        word_count = len(transcript.split())
        model_used = st.session_state.get("llm_model", AVAILABLE_LLM_MODELS[0])

        duration = st.session_state.duration_seconds or 0
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        length_display = f"{minutes}:{seconds:02d}"

        if st.session_state.meeting_title:
            st.subheader(st.session_state.meeting_title)

        stat_cols = st.columns(4)
        stat_cols[0].metric("Word Count", f"{word_count:,}")
        stat_cols[1].metric("Length", length_display)
        stat_cols[2].metric("Action Items", len(st.session_state.action_items or []))
        stat_cols[3].metric("Language", (st.session_state.detected_language or "N/A").upper())

        st.download_button(
            "Download Transcript",
            data=transcript,
            file_name="transcript.txt",
            mime="text/plain",
        )

        tabs = st.tabs(
            ["Transcript", "Summary", "Action Items", "Topics and Decisions",
             "Ask Questions", "Follow-up Email", "Full Report"]
        )

        with tabs[0]:
            view_choice = st.radio(
                "View", ["Timestamped", "Full Text"], horizontal=True, label_visibility="collapsed"
            )
            if view_choice == "Timestamped":
                if st.session_state.audio_bytes and st.session_state.segments:
                    player_html = build_player_html(
                        st.session_state.audio_bytes,
                        st.session_state.audio_mime,
                        st.session_state.segments,
                    )
                    st.components.v1.html(player_html, height=520, scrolling=False)
                else:
                    st.write(transcript)
            else:
                escaped_transcript = html.escape(transcript).replace("\n", "<br>")
                st.markdown(
                    f"""
                    <div style="max-height:420px; overflow-y:auto; border:1px solid #444;
                                 border-radius:6px; padding:16px; color:#FAFAFA;
                                 font-family:sans-serif; line-height:1.6;">
                        {escaped_transcript}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tabs[1]:
            st.write(st.session_state.summary or "No summary generated yet.")

        with tabs[2]:
            items = st.session_state.action_items
            if items:
                st.table(items)
                ics_data = build_ics(items)
                st.download_button(
                    "Download Calendar File",
                    data=ics_data,
                    file_name="action_items.ics",
                    mime="text/calendar",
                )
                st.caption(
                    "Only items with a recognizable deadline are included. "
                    "Vague deadlines like 'soon' cannot be converted to a calendar date."
                )
            else:
                st.info("No action items were detected in this meeting.")

        with tabs[3]:
            td = st.session_state.topics_decisions or {}
            topics = td.get("topics", [])
            decisions = td.get("decisions", [])

            st.markdown("Topics Discussed")
            if topics:
                for i, topic in enumerate(topics, start=1):
                    with st.expander(f"Topic {i}: {topic.get('title', 'Untitled')}"):
                        st.write(topic.get("summary", ""))
            else:
                st.info("No distinct topics were detected.")

            st.markdown("Key Decisions")
            if decisions:
                for d in decisions:
                    st.markdown(f"- {d}")
            else:
                st.info("No clear decisions were detected in this meeting.")

        with tabs[4]:
            st.caption("Answers are grounded strictly in the transcript.")
            question = st.text_input("Your question", key="qna_input")
            if st.button("Ask"):
                if question.strip():
                    with st.spinner("Finding the answer..."):
                        answer = answer_question(transcript, question, model=model_used)
                        st.session_state.qna_history.append((question, answer))
                else:
                    st.warning("Please type a question first.")

            for q, a in reversed(st.session_state.qna_history):
                st.markdown(f"Q: {q}")
                st.markdown(a)
                st.divider()

        with tabs[5]:
            if st.button("Generate Follow-up Email"):
                with st.spinner("Drafting email..."):
                    td = st.session_state.topics_decisions or {}
                    st.session_state.email_text = generate_followup_email(
                        summary=st.session_state.summary or "",
                        decisions=td.get("decisions", []),
                        action_items=st.session_state.action_items or [],
                        model=model_used,
                    )

            if "email_text" in st.session_state:
                st.text_area("Generated Email", st.session_state.email_text, height=300)
                st.download_button(
                    "Download Email as Text File",
                    data=st.session_state.email_text,
                    file_name="meeting_followup_email.txt",
                    mime="text/plain",
                )

        with tabs[6]:
            td = st.session_state.topics_decisions or {}
            items = st.session_state.action_items or []
            title = st.session_state.meeting_title or "Meeting Report"

            report_lines = [
                f"# {title}",
                "",
                f"Word count: {word_count:,}  |  Length: {length_display}  |  "
                f"Language: {(st.session_state.detected_language or 'N/A').upper()}",
                "",
                "## Summary",
                st.session_state.summary or "N/A",
                "",
                "## Key Decisions",
            ]
            report_lines += [f"- {d}" for d in td.get("decisions", [])] or ["None recorded."]

            report_lines += ["", "## Topics Discussed"]
            for t in td.get("topics", []):
                report_lines.append(f"{t.get('title', 'Untitled')} - {t.get('summary', '')}")

            report_lines += ["", "## Action Items"]
            if items:
                for item in items:
                    report_lines.append(
                        f"- {item.get('task', 'N/A')} "
                        f"(Assignee: {item.get('assignee', 'Unassigned')}, "
                        f"Deadline: {item.get('deadline', 'Not specified')}, "
                        f"Priority: {item.get('priority', 'N/A')})"
                    )
            else:
                report_lines.append("None recorded.")

            report_lines += ["", "## Full Transcript", transcript]
            full_report = "\n".join(report_lines)

            report_col1, report_col2 = st.columns(2)
            with report_col1:
                st.download_button(
                    "Download Full Report (Markdown)",
                    data=full_report,
                    file_name="meeting_report.md",
                    mime="text/markdown",
                )
            with report_col2:
                pdf_bytes = build_pdf_report(
                    title=title,
                    summary=st.session_state.summary or "",
                    decisions=td.get("decisions", []),
                    topics=td.get("topics", []),
                    action_items=items,
                    transcript=transcript,
                )
                st.download_button(
                    "Download Full Report (PDF)",
                    data=pdf_bytes,
                    file_name="meeting_report.pdf",
                    mime="application/pdf",
                )
    else:
        st.info("Upload an audio file on the left and click Submit to get started.")