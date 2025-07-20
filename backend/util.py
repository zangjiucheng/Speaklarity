from werkzeug.datastructures.file_storage import FileStorage
import json
import subprocess
import os
import time

def save_info_to_file(file_path: str, data: dict) -> None:
    """
    Save a dictionary to a JSON file.
    
    :param file_path: Path to the output JSON file
    :param data: Dictionary to save
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_info_to_index(index_path: str, new_json: dict) -> dict:
    """
    Add metadata to the index file.
    """
    try:
        # Read existing index
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Update index with new data
        index_data.update(new_json)
        
        # Write updated index back to file
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        return index_data
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Index file {index_path} not found.")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the index file.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while updating the index: {str(e)}")

def save_audio_to_wav(input_file, output_path: str) -> str:
    """
    Save an uploaded audio file and convert it to WAV format using ffmpeg.
    Returns the path to the converted WAV file.
    """
    temp_input_path = output_path + "_temp_input"
    if isinstance(input_file, FileStorage):
        input_file.save(temp_input_path)
    elif isinstance(input_file, str):
        temp_input_path = input_file
    else:
        raise ValueError("input_file must be a FileStorage object or a file path string.")

    try:
        # subprocess.run waits for the process to complete by default
        subprocess.run(
            ['ffmpeg', '-y', '-i', temp_input_path, '-ar', '16000', '-ac', '1', output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        os.remove(temp_input_path)
        print(f"Audio converted and saved to {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        os.remove(temp_input_path)
        raise RuntimeError(f"Audio conversion failed: {e.stderr.decode('utf-8')}")


def play_audio_segment(audio_path: str, start_time: float, end_time: float) -> None:
    """
    Play a segment of an audio file from start_time to end_time (in seconds).
    Requires ffplay (part of ffmpeg) to be installed.
    """
    duration = end_time - start_time
    if duration <= 0:
        raise ValueError("end_time must be greater than start_time.")
    try:
        subprocess.run(
            [
                'ffplay',
                '-nodisp',
                '-autoexit',
                '-ss', str(start_time),
                '-t', str(duration),
                audio_path
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio playback failed: {e}")

def synthesize_native(text: str, out_wav: str, engine: str = "coqui"):
    """
    Generate a native‑speaker WAV file for `text` and save it to `out_wav`.

    • engine="coqui"  ->  offline Coqui‑TTS (pip install TTS)
    • engine="gtts"   ->  Google TTS (requires internet, pip install gTTS pydub)
    • engine="openai" ->  OpenAI TTS (needs API key, pip install openai)
    """
    if engine == "coqui":
        from TTS.api import TTS
        # any English single‑speaker model works; this one sounds neutral/native
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC_ph").to("cpu")
        tts.tts_to_file(text=text, file_path=out_wav, speaker_wav=None)
    elif engine == "gtts":
        from gtts import gTTS
        tmp_mp3 = out_wav + ".mp3"
        gTTS(text, lang="en", tld="com").save(tmp_mp3)
        save_audio_to_wav(tmp_mp3, out_wav)
    elif engine == "openai":
        import openai, soundfile as sf
        audio = openai.audio.speech.create(model="tts-1", voice="alloy", input=text)
        # audio.audio is bytes in WAV format
        with open(out_wav, "wb") as f:
            f.write(audio.audio)
    else:
        raise ValueError(f"Unknown TTS engine '{engine}'")

def cut_audio(input_path: str, output_path: str, start: float, end: float):
    """
    Cut a segment from an audio file and save it to output_path.
    Uses ffmpeg to handle the audio processing.
    """
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        subprocess.run(
            ['ffmpeg', '-y', '-i', input_path, '-ss', str(start), '-to', str(end), output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Audio segment saved to {output_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio cutting failed: {e.stderr.decode('utf-8')}")

if __name__ == "__main__":
    synthesize_native(
        "This is a test sentence for the native speaker audio generation.",
        "native_speaker.wav",
        engine="gtts"
    )

# if __name__ == "__main__":
#     # Example usage
#     audio_file = "data/644bebe899c244f5/conversation_644bebe899c244f5.wav"  # Replace with your audio file path
#     start = 3.67  # Start time in seconds
#     end = 6.11    # End time in seconds

#     try:
#         play_audio_segment(audio_file, start, end)
#     except Exception as e:
#         print(f"Error: {e}")