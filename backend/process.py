from torch._dynamo.polyfills import index
import json
import re

import align_text, accent_check
import util
import subprocess

TTS_ENGINE = "gtts"  # Default TTS engine
VISUALIZE = False  # Default visualization setting

def split_conversation_to_sentences(conversation_id: str) -> bool:
    conversation_path = f"data/{conversation_id}/conversation_{conversation_id}.wav"

    audio_info = align_text.load_wav_info(conversation_path)
    print(f"Audio length: {audio_info[0]:.1f}s")

    tl = align_text.make_timeline(conversation_path)

    index_path = f"data/{conversation_id}/index.json"
    util.add_info_to_index(index_path, {"sentences": tl})

    return True

def score_accent(
    conversation_id: str,
    sr: int = 16000,
):
    """
    Score the user's audio against a native reference.
    If `native_audio_path` is None, it will be auto-generated.
    Returns (word_scores, sentence_score).
    """

    user_audio_path = f"data/{conversation_id}/conversation_{conversation_id}.wav"

    # Load sentence timeline from index.json
    index_path = f"data/{conversation_id}/index.json"
    with open(index_path, "r") as f:
        index_data = json.load(f)
    sentences = index_data.get("sentences", [])

    if not sentences:
        raise ValueError("No sentences found in index.json")

    # Cut user_audio_path into sentence audio files
    sentence_audios = []
    for i, sentence in enumerate(sentences):
        # Extract audio timeline for the sentence
        audio_timeline = sentence.get("audio_timeline", None)
        if not audio_timeline:
            raise ValueError(f"No audio timeline found for sentence {i+1}")
        # You can use audio_timeline as needed here
        start, end = audio_timeline["start"], audio_timeline["end"]
        sentence_audio_path = f"data/{conversation_id}/sentences/sentence_{i}.wav"
        util.cut_audio(user_audio_path, sentence_audio_path, start, end)
        sentence_audios.append((i+1,sentence_audio_path))

        # DEBUG: Print extracted sentence audio paths
        # print(f"Extracted sentence audio: {sentence_audios}")
    
    for sentence_audio in sentence_audios:
        index, user_audio_path = sentence_audio

        print(f"Scoring sentence {index + 1} with audio {user_audio_path}")

        # Score each sentence
        word_scores, sentence_score = accent_check.score_sentence(
            user_audio_path=user_audio_path,
            native_audio_path=None,  # Auto-generate native audio
            sr=sr,
            tts_engine=TTS_ENGINE,
            visualize=VISUALIZE,
        )

        # DEBUG: Print scores for verification
        print("Word Scores:", word_scores)
        print("Sentence Score:", sentence_score)

        # Save scores to index.json
        # Find the sentence with matching 'id' == index and update scores
        for s in index_data["sentences"]:
            if s.get("id") == index:
                s["word_scores"] = word_scores
                s["sentence_score"] = sentence_score
                index_data["sentences"].remove(s)
                index_data["sentences"].append(s)
                break

    util.save_info_to_file(index_path, index_data)

    return True

def pipeline(conversation_id: str) -> None:
    """
    Process the conversation by splitting it into sentences and scoring each sentence.
    """
    if not split_conversation_to_sentences(conversation_id):
        raise RuntimeError(f"Failed to process conversation {conversation_id}")

    # Example usage of scoring accent
    user_audio_path = f"data/{conversation_id}/conversation_{conversation_id}.wav"

    if not score_accent(conversation_id):
        raise RuntimeError(f"Failed to score accent for conversation {conversation_id}")

if __name__ == "__main__":
    # Example usage
    conversation_id = "644bebe899c244f5"  # Replace with your conversation ID
    split_conversation_to_sentences(conversation_id)
    score_accent(conversation_id, sr=16000)