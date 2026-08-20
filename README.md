# Meeting Summarizer

An AI-powered meeting assistant that turns raw meeting audio into a structured, actionable record — transcript, summary, action items, decisions, and a ready-to-send follow-up email — all from a single Streamlit app.

## Features

- **Transcription** of meeting audio (MP3, WAV, M4A) using `faster-whisper`, with automatic language detection and optional translation to English
- **Auto-generated meeting title** based on the transcript content
- **AI summary** covering what was discussed and decided
- **Structured action items** — task, assignee, deadline, priority, and status — extracted directly from the conversation
- **Topics & decisions view** — key discussion points broken into expandable sections, plus a clean list of decisions made
- **Meeting Q&A** — ask free-form questions, answered strictly from the transcript to avoid hallucination
- **Follow-up email generator** — drafts a send-ready recap email from the summary, decisions, and action items
- **Dual transcript view** — a clickable, timestamped transcript that jumps the audio player to that moment, or a plain full-text view
- **Calendar export (.ics)** for action items with a recognizable deadline
- **Full report export** in both Markdown and PDF
- **Session-only storage** — nothing is persisted beyond the current browser session

## Tech Stack

| Component | Technology |
|---|---|
| App framework | Streamlit |
| Speech-to-text | `faster-whisper` (runs locally, CPU, int8) |
| Language model | Groq API (`openai/gpt-oss-20b` or `openai/gpt-oss-120b`, selectable in-app) |
| Calendar export | `python-dateutil` + a hand-built `.ics` writer |
| PDF export | `reportlab` |
| Storage | In-memory Streamlit session state — no database |

## Project Structure

```
meeting-summarizer/
├── app.py                     # Streamlit UI and app flow
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml            # Dark theme config
├── sample_audio/              # Drop a test recording here
└── utils/
    ├── audio_handler.py       # Temp file save/cleanup for uploads
    ├── audio_player.py        # Custom HTML5 player synced to transcript timestamps
    ├── transcriber.py         # faster-whisper wrapper
    ├── groq_client.py         # Groq API client + JSON-safe parsing
    ├── chunking.py            # Splits long transcripts, ranks chunks for Q&A
    ├── summarizer.py          # Meeting summary generation
    ├── action_items.py        # Action item extraction
    ├── topics_decisions.py    # Topic and decision extraction
    ├── qna.py                 # Transcript-grounded question answering
    ├── email_generator.py     # Follow-up email drafting
    ├── meeting_title.py       # Meeting title generation
    ├── calendar_export.py     # .ics file builder
    └── pdf_export.py          # PDF report builder
```

## Getting Started

### 1. Clone and enter the project

```bash
git clone https://github.com/princebhandarii/Meeting-Summarizer.git
cd meeting-summarizer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy the example env file and add your Groq API key (free tier available at [console.groq.com/keys](https://console.groq.com/keys)):

```bash
cp .env.example .env
```

```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

### 6. Use it

Upload a meeting recording, optionally add context (e.g. "Weekly product marketing sync with the growth team"), pick a Whisper model and an LLM model, then click **Submit**. Results appear across the Transcript, Summary, Action Items, Topics & Decisions, Q&A, Follow-up Email, and Full Report tabs.

## Configuration Options

| Setting | Options | Notes |
|---|---|---|
| Language handling | Auto-detect / Translate to English | Applies during transcription |
| Whisper model | `tiny`, `base`, `small` | Larger = more accurate, slower, more RAM |
| LLM model | `openai/gpt-oss-20b`, `openai/gpt-oss-120b` | 20b is faster; 120b is more capable |

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub (public, `main` branch)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect the repo
3. Set `app.py` as the entry point
4. Add `GROQ_API_KEY` under **App Settings → Secrets**
5. Deploy

> Keep the Whisper model set to `tiny` or `base` for deployment — larger models may not fit in the free tier's memory limit.

## Notes

- The `base` Whisper model is the default balance of accuracy and memory usage for free hosting
- No transcript or meeting data is stored beyond the current browser session
- Action items with vague deadlines (e.g. "soon") are skipped in the calendar export, since they can't be converted into a real date
- Meeting length shown in the app reflects actual audio duration, not an estimate
- All LLM prompts are written to stay grounded in the transcript to reduce hallucination, especially for Q&A

## License

Add your preferred license here (e.g. MIT).
