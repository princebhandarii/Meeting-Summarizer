import os
import tempfile


def save_temp_audio(file_bytes, filename):
    ext = os.path.splitext(filename)[1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_file.write(file_bytes)
    temp_file.close()
    return temp_file.name


def cleanup_temp_audio(file_path):
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
