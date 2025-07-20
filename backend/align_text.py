from pathlib import Path
import json
import re
import soundfile as sf
import torch
from whisper_timestamped import load_model, transcribe

def load_wav_info(path: str):
    """Return length (s) and sample‑rate for sanity checks."""
    info = sf.info(path)
    return info.frames / info.samplerate, info.samplerate

def sentence_chunks(words, sent_end_re=r"[.!?…]+"):
    """
    Group word dicts (with 'text','start','end') into sentences.
    Yields (sentence_text, start_t, end_t).
    """
    buf, start_t = [], None
    for w in words:
        if start_t is None:
            start_t = w["start"]
        buf.append(w["text"])
        if re.search(sent_end_re, w["text"]):
            end_t = w["end"]
            yield " ".join(buf).strip(), start_t, end_t
            buf, start_t = [], None
    # trailing words without punctuation
    if buf:
        yield " ".join(buf).strip(), start_t, words[-1]["end"]

def make_timeline(audio_path: str,
                  model_name: str = "medium.en",
                  device: str = "cuda" if torch.cuda.is_available() else "cpu"):
    """
    Return list of dicts: id, sentence_text, audio_timeline
    """
    model = load_model(model_name, device=device)
    # we only need word‑level info, so set `return_segments=True`
    result = transcribe(model, audio_path, language="en", vad=True)
    words = [w for seg in result["segments"] for w in seg["words"]]

    timeline: list[dict] = []
    for idx, (text, t0, t1) in enumerate(sentence_chunks(words), start=1):
        timeline.append(
            {"id": idx,
             "sentence_text": text,
             "audio_timeline": {"start": round(t0, 2), "end": round(t1, 2)}}
        )
    return timeline

if __name__ == "__main__":
    wav = "data/31a5da64070d46c4/conversation_31a5da64070d46c4.wav"
    # wav = "audio3.wav"  # replace with your audio file
    print(f"Audio length: {load_wav_info(wav)[0]:.1f}s")
    tl = make_timeline(wav)
    print(json.dumps(tl, indent=2, ensure_ascii=False))
