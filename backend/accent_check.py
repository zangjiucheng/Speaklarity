import os, tempfile, torch, torchaudio, whisper, torch.nn.functional as F
from torchaudio.pipelines import WAVLM_LARGE
import matplotlib.pyplot as plt
import util

device: str = "cpu"
whisper_model = whisper.load_model("base.en", device=device)


# --- Audio Preprocessing ---
def normalize_rms(wav, target_rms=0.1):
    rms = wav.pow(2).mean().sqrt()
    if rms > 0:
        wav = wav * (target_rms / rms)
    return wav

def highpass_filter(wav, sr, cutoff=80):
    # Remove low-frequency rumble/noise
    return torchaudio.functional.highpass_biquad(wav, sr, cutoff)

def preprocess_wav(path, sr, cutoff=80, target_rms=0.1):
    wav, s = torchaudio.load(path)
    wav = torchaudio.transforms.Resample(s, sr)(wav).mean(0, keepdim=True)
    wav = highpass_filter(wav, sr, cutoff)
    wav = normalize_rms(wav, target_rms)

    # Save the processed waveform to a temporary WAV file for inspection/debugging
    # temp_wav_path = path.replace(".wav", "_processed.wav")
    # torchaudio.save(temp_wav_path, wav, sr)
    return wav

# --------------- main scorer -----------------
def score_sentence(
    user_audio_path: str,
    native_audio_path: str | None = None,
    native_txt: str = "",
    sr: int = 16000,
    tts_engine: str = "gtts",
    visualize: bool = True,
):
    """
    If `native_audio_path` is None, a native reference is auto‑generated from
    the user's transcribed text via TTS (chosen by `tts_engine`).
    Returns (word_scores, sentence_score).
    If any error occurs, returns a below average score and logs the error.
    """
    try:
        # Whisper forced alignment
        result = whisper_model.transcribe(
            user_audio_path, word_timestamps=True, language="en",
            condition_on_previous_text=False,
        )
        words = [
            {"word": w["word"].strip(), "start": w["start"], "end": w["end"]}
            for seg in result["segments"] for w in seg["words"]
        ]

        # Produce native reference if needed
        if native_audio_path is None:
            native_audio_path = user_audio_path.replace(".wav", "_native.wav")
            util.synthesize_native(native_txt, native_audio_path, engine=tts_engine)

        # Load, filter, and normalize both clips
        user_wav = preprocess_wav(user_audio_path, sr)
        native_wav = preprocess_wav(native_audio_path, sr)

        # WavLM embeddings
        wavlm = WAVLM_LARGE.get_model().to(device).eval()
        @torch.no_grad()
        def emb(w):  # mean‑pooled last‑layer embedding
            feats, _ = wavlm.extract_features(w.to(device))
            return feats[-1].mean(1)

        native_emb = emb(native_wav)

        # helper to slice word audio
        def slice_word(wav, start, end):
            return wav[:, int(start * sr): int(end * sr)]

        # Score words
        word_scores = []
        for w in words:
            clip = slice_word(user_wav, w["start"], w["end"])
            if clip.shape[1] < 160:            # too short → skip
                continue
            s = torch.nn.functional.cosine_similarity(emb(clip), native_emb).item()
            word_scores.append({"word": w["word"], "score": s})
        sentence_score = float(torch.tensor([ws["score"] for ws in word_scores]).mean())

        # Improved visualization
        if visualize and word_scores:
            labs, vals = zip(*[(w["word"], w["score"]) for w in word_scores])
            colors = ["#4CAF50" if v >= .5 else "#FFC107" if v >= .3 else "#F44336" for v in vals]  # better color palette
            fig, ax = plt.subplots(figsize=(max(8, len(labs)), 4))
            bars = ax.bar(labs, vals, color=colors, edgecolor="black", linewidth=0.7)
            ax.axhline(.3, ls="--", c="gray", label="Needs improvement")
            ax.axhline(.5, ls="--", c="blue", label="Good pronunciation")
            ax.set_ylim(0, 1)
            ax.set_xticks(range(len(labs)))
            ax.set_xticklabels(labs, rotation=45, ha="right", fontsize=10)
            ax.set_ylabel("Cosine similarity", fontsize=12)
            ax.set_title("Word-by-word Pronunciation Score", fontsize=14)
            ax.legend()
            fig.tight_layout()

            # Annotate bars with score values
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                        f"{val:.2f}", ha="center", va="bottom", fontsize=9)

            plt.show()

        # cleanup temp file if we created one
        if "fp" in locals():
            os.unlink(native_audio_path)

        return word_scores, sentence_score
    except Exception as e:
        import logging
        logging.error(f"Accent scoring failed: {e}")
        # Return a below average score and empty word_scores
        return [], 0.25

if __name__ == "__main__":
    # Example usage
    user_audio_path = "sentence_11.wav"  # Replace with your audio file path
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