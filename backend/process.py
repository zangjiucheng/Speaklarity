import json
import re
import os
from pathlib import Path
import logging
import align_text, accent_check, grammar_check_gemini, grammar_check_openai
import util
import subprocess
import socketio

GRAMMAR_CHECK_AI = os.getenv("GRAMMAR_CHECK_AI", "gemini").lower()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Configuration via environment variables
TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")  # Default TTS engine
VISUALIZE = os.getenv("VISUALIZE", "False").lower() == "true"  # Default visualization setting

# In your pipeline or after status changes:
def notify_status(socketio, conv_id, status):
    socketio.emit('status', {'id': conv_id, 'status': status})

def split_conversation_to_sentences(conversation_id: str) -> bool:
    """
    Split the conversation audio into sentences and create an index.json file.

    This function processes the audio file associated with the given conversation_id,
    extracts sentence boundaries using forced alignment, and stores sentence metadata
    (including timing information) in an index.json file for downstream processing.

    Returns:
        True if successful, False otherwise.
    """
    conversation_path = Path("data") / conversation_id / f"conversation_{conversation_id}.wav"
    try:
        index_path = Path("data") / conversation_id / "index.json"
        with open(index_path, "r") as f:
            index_data = json.load(f)
        index_data["action"] = "splitting"
        util.save_info_to_file(str(index_path), index_data)
        audio_info = align_text.load_wav_info(str(conversation_path))
        logging.info(f"Audio length: {audio_info[0]:.1f}s")
        tl = align_text.make_timeline(str(conversation_path))
        util.add_info_to_index(str(index_path), {"sentences": tl})
        return True
    except Exception as e:
        logging.error(f"Error splitting conversation: {e}")
        return False

def score_accent(conversation_id: str, sr: int = 16000) -> bool:
    """
    Score the user's audio for accent accuracy on a sentence-by-sentence basis.

    This function processes each sentence audio segment extracted from the user's conversation,
    compares it against a native reference (auto-generated if not provided), and computes
    both word-level and sentence-level accent scores using the configured TTS engine.

    Args:
        conversation_id (str): Unique identifier for the conversation.
        sr (int, optional): Sample rate for audio processing. Defaults to 16000.

    Returns:
        bool: True if scoring is successful for all sentences, False otherwise.

    Logs detailed information and errors for each step, including per-sentence scoring results.
    """
    user_audio_path = Path("data") / conversation_id / f"conversation_{conversation_id}.wav"
    index_path = Path("data") / conversation_id / "index.json"
    try:
        with open(index_path, "r") as f:
            index_data = json.load(f)
        index_data["action"] = "scoring"
        util.save_info_to_file(str(index_path), index_data)
        sentences = index_data.get("sentences", [])
        if not sentences:
            logging.error("No sentences found in index.json")
            return False
        sentence_audios = []
        for i, sentence in enumerate(sentences):
            audio_timeline = sentence.get("audio_timeline", None)
            if not audio_timeline:
                logging.error(f"No audio timeline found for sentence {i+1}")
                return False
            start, end = audio_timeline["start"], audio_timeline["end"]
            sentence_audio_path = Path("data") / conversation_id / "sentences" / f"sentence_{i}.wav"
            util.cut_audio(str(user_audio_path), str(sentence_audio_path), start, end)
            sentence_audios.append((i+1, str(sentence_audio_path)))
        for sentence_audio in sentence_audios:
            index, user_audio_path = sentence_audio
            logging.info(f"Scoring sentence {index} with audio {user_audio_path}")
            # Find the sentence in sentences where s["id"] == index
            native_txt = ""
            for s in sentences:
                if s.get("id") == index:
                    native_txt = s.get("sentence_text", "")
                    break
            word_scores, sentence_score = accent_check.score_sentence(
                user_audio_path=user_audio_path,
                native_audio_path=None,
                native_txt=native_txt,
                sr=sr,
                tts_engine=TTS_ENGINE,
                visualize=VISUALIZE,
            )
            logging.info(f"Word Scores: {word_scores}")
            logging.info(f"Sentence Score: {sentence_score}")
            for s in index_data["sentences"]:
                if s.get("id") == index:
                    s["word_scores"] = word_scores
                    s["sentence_score"] = sentence_score
                    index_data["sentences"].remove(s)
                    index_data["sentences"].append(s)
                    break
        util.save_info_to_file(str(index_path), index_data)
        return True
    except Exception as e:
        logging.error(f"Error scoring accent: {e}")
        return False

def grammar_check_with_ai(conversation_id: str) -> bool:
    """
    Perform AI-powered grammar analysis for each sentence in the conversation.

    This function loads sentence data from index.json, analyzes grammar using an AI model,
    and updates each sentence entry with grammar feedback. Results are saved back to index.json.

    Returns:
        bool: True if grammar analysis is successful for all sentences, False otherwise.

    Logs detailed information and errors for each step, including per-sentence grammar results.
    """
    index_path = Path("data") / conversation_id / "index.json"
    try:
        with open(index_path, "r") as f:
            index_data = json.load(f)
        index_data["action"] = "checking grammar"
        util.save_info_to_file(str(index_path), index_data)
        sentences = index_data.get("sentences", [])
        if not sentences:
            logging.error("No sentences found in index.json")
            return False
        for sentence in sentences:
            index = sentence.get("id")
            if index is None:
                logging.error(f"Sentence {sentence} does not have a valid 'id' field")
                return False
            text_content = sentence.get("sentence_text", "")
            if not text_content:
                continue
            if GRAMMAR_CHECK_AI == "gemini":
                grammar_analysis = grammar_check_gemini.analyze_grammar(text_content)
            elif GRAMMAR_CHECK_AI == "openai":
                grammar_analysis = grammar_check_openai.analyze_grammar(text_content)
            else:
                logging.error(f"Unsupported grammar check AI: {GRAMMAR_CHECK_AI}")
                return False
            logging.info(f"Grammar Analysis for Sentence {index}: {grammar_analysis}")
            for s in index_data["sentences"]:
                if s.get("id") == index:
                    s["grammar_analysis"] = grammar_analysis
                    break
        util.save_info_to_file(str(index_path), index_data)
        return True
    except Exception as e:
        logging.error(f"Error in grammar check: {e}")
        return False

def pipeline(conversation_id: str, socketio=None):
    """
    Orchestrates the full processing pipeline for a conversation.

    Steps:
        1. Splits the conversation audio into sentences and generates sentence metadata.
        2. Scores each sentence for accent accuracy using the configured TTS engine.
        3. Performs AI-powered grammar analysis for each sentence.
        4. Logs progress and errors at each stage.

    Args:
        conversation_id (str): Unique identifier for the conversation.

    Returns:
        None
    """
    
    logging.info(f"Starting pipeline for conversation {conversation_id}")
    if socketio:
        notify_status(socketio, conversation_id, "splitting")
    if not split_conversation_to_sentences(conversation_id):
        logging.error(f"Failed to process conversation {conversation_id}")
        return
    if socketio:
        notify_status(socketio, conversation_id, "scoring")
    logging.info(f"Scoring accent for conversation {conversation_id}")
    if not score_accent(conversation_id):
        logging.error(f"Failed to score accent for conversation {conversation_id}")
        return
    if socketio:
        notify_status(socketio, conversation_id, "checking grammar")
    if not grammar_check_with_ai(conversation_id):
        logging.error(f"Failed to check grammar for conversation {conversation_id}")
        return
    logging.info(f"Pipeline completed for conversation {conversation_id}")

    index_path = Path("data") / conversation_id / "index.json"
    try:
        with open(index_path, "r") as f:
            index_data = json.load(f)
        index_data["action"] = "finished"
        index_data["summary"] = " ".join(
            s.get("sentence_text", "") for s in index_data.get("sentences", [])
        )[:50] # Truncate to 50 characters
        util.save_info_to_file(str(index_path), index_data)
        if socketio:
            notify_status(socketio, conversation_id, "finished")
    except Exception as e:
        logging.error(f"Error finalizing index.json: {e}")

if __name__ == "__main__":
    # Example usage
    conversation_id = "6aa7a6d200024c5c"  # Replace with your conversation ID
    pipeline(conversation_id)