import os, tempfile, torch, torchaudio, whisper, torch.nn.functional as F
from torchaudio.pipelines import WAVLM_LARGE
import matplotlib.pyplot as plt
import util

device: str = "cpu"
whisper_model = whisper.load_model("base", device=device)

# --------------- main scorer -----------------
def score_sentence(
    user_audio_path: str,
    native_audio_path: str | None = None,
    sr: int = 16000,
    tts_engine: str = "gtts",
    visualize: bool = True,
):
    """
    If `native_audio_path` is None, a native reference is auto‑generated from
    the user's transcribed text via TTS (chosen by `tts_engine`).
    Returns (word_scores, sentence_score).
    """
    # 1️⃣  Whisper forced alignment
    result = whisper_model.transcribe(
        user_audio_path, word_timestamps=True, language="en",
        condition_on_previous_text=False,
    )
    words = [
        {"word": w["word"].strip(), "start": w["start"], "end": w["end"]}
        for seg in result["segments"] for w in seg["words"]
    ]
    full_text = " ".join(w["word"] for w in words)

    # 2️⃣  Produce native reference if needed
    if native_audio_path is None:
        # NOTE: we could use a temp file here, but we want to keep the native audio
        # fp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        # native_audio_path = fp.name
        native_audio_path = user_audio_path.replace(".wav", "_native.wav")
        util.synthesize_native(full_text, native_audio_path, engine=tts_engine)

    # 3️⃣  Load + resample both clips
    def load_mono(path):
        wav, s = torchaudio.load(path)
        return torchaudio.transforms.Resample(s, sr)(wav).mean(0, keepdim=True)

    user_wav = load_mono(user_audio_path)
    native_wav = load_mono(native_audio_path)

    # 4️⃣  WavLM embeddings
    wavlm = WAVLM_LARGE.get_model().to(device).eval()
    @torch.no_grad()
    def emb(w):  # mean‑pooled last‑layer embedding
        feats, _ = wavlm.extract_features(w.to(device))
        return feats[-1].mean(1)

    native_emb = emb(native_wav)

    # helper to slice word audio
    def slice_word(wav, start, end):
        return wav[:, int(start * sr): int(end * sr)]

    # 5️⃣  Score words
    word_scores = []
    for w in words:
        clip = slice_word(user_wav, w["start"], w["end"])
        if clip.shape[1] < 160:            # too short → skip
            continue
        s = torch.nn.functional.cosine_similarity(emb(clip), native_emb).item()
        word_scores.append({"word": w["word"], "score": s})
    sentence_score = float(torch.tensor([ws["score"] for ws in word_scores]).mean())

    # 6️⃣  optional viz (same as before) …
    if visualize and word_scores:
        labs, vals = zip(*[(w["word"], w["score"]) for w in word_scores])
        colors = ["green" if v >= .95 else "orange" if v >= .85 else "red" for v in vals]
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.bar(labs, vals, color=colors)
        ax.axhline(.85, ls="--", c="gray", label="Needs improvement")
        ax.axhline(.95, ls="--", c="blue", label="Good pronunciation")
        ax.set_ylim(0, 1)
        ax.set_xticks(range(len(labs)))
        ax.set_xticklabels(labs, rotation=45)
        ax.set_ylabel("Cosine similarity")
        ax.set_title("Word‑by‑word pronunciation score")
        ax.legend()
        fig.tight_layout()
        plt.show()

    # cleanup temp file if we created one
    if "fp" in locals():
        os.unlink(native_audio_path)

    return word_scores, sentence_score

if __name__ == "__main__":
    # Example usage
    user_audio_path = "audio3.wav"  # Replace with your audio file path
    native_audio_path = None  # Auto-generate native audio
    sr = 16000  # Sample rate
    tts_engine = "gtts"  # TTS engine to use
    visualize = True  # Whether to visualize the results
    word_scores, sentence_score = score_sentence(
        user_audio_path=user_audio_path,
        native_audio_path=native_audio_path,
        sr=sr,
        tts_engine=tts_engine,
        visualize=visualize,
    )