import base64
import html


def guess_mime(filename):
    ext = filename.lower().rsplit(".", 1)[-1]
    return {"mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4"}.get(ext, "audio/mpeg")


def build_player_html(audio_bytes, mime_type, segments):
    encoded = base64.b64encode(audio_bytes).decode()

    rows = []
    for seg in segments:
        minutes = int(seg["start"] // 60)
        seconds = int(seg["start"] % 60)
        timestamp = f"{minutes}:{seconds:02d}"
        text = html.escape(seg.get("text", ""))
        speaker = seg.get("speaker")
        label = f"{html.escape(speaker)}: " if speaker else ""
        rows.append(
            f'<div class="segment-row" onclick="jumpTo({seg["start"]})">'
            f'<span class="segment-time">{timestamp}</span>'
            f'<span class="segment-text">{label}{text}</span>'
            f'</div>'
        )

    segment_html = "".join(rows)

    return f"""
    <audio id="meetingAudioPlayer" controls style="width:100%; margin-bottom:12px;">
        <source src="data:{mime_type};base64,{encoded}" type="{mime_type}">
    </audio>
    <div style="max-height:420px; overflow-y:auto; border:1px solid #444; border-radius:6px; padding:8px;">
        {segment_html}
    </div>
   <style>
    body {{
        color: #FAFAFA;
        font-family: sans-serif;
        margin: 0;
    }}
    .segment-row {{
        display:flex;
        gap:10px;
        padding:6px;
        cursor:pointer;
        border-bottom:1px solid #333;
        color: #FAFAFA;
    }}
    .segment-row:hover {{
        background-color: rgba(128,128,128,0.15);
    }}
    .segment-time {{
        font-weight:bold;
        min-width:50px;
        color: #FAFAFA;
    }}
</style>
    <script>
        function jumpTo(seconds) {{
            var audio = document.getElementById('meetingAudioPlayer');
            audio.currentTime = seconds;
            audio.play();
        }}
    </script>
    """
