from faster_whisper import WhisperModel

_models = {}


def _get_model(model_size="base"):
    if model_size not in _models:
        _models[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _models[model_size]


def transcribe_audio(file_path, model_size="base", translate=False):
    model = _get_model(model_size)
    task = "translate" if translate else "transcribe"
    segments_gen, info = model.transcribe(file_path, beam_size=5, task=task)

    segments = []
    text_parts = []
    for seg in segments_gen:
        text = seg.text.strip()
        segments.append({"start": seg.start, "end": seg.end, "text": text})
        text_parts.append(text)

    return {
        "text": " ".join(text_parts),
        "segments": segments,
        "language": info.language,
        "duration": info.duration,
    }
