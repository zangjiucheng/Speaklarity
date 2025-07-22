from werkzeug.datastructures.file_storage import FileStorage
from flask import Flask, jsonify, send_from_directory, request, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
import hashlib, json, os, uuid
from pathlib import Path
from datetime import datetime, timezone
import time

from process import pipeline
from util import save_audio_to_wav
import threading
import shutil
from flask_socketio import SocketIO, emit

UPLOAD_ROOT = Path("data")
ALLOWED_EXT = {".wav"}
MAX_BYTES   = 25 * 1024 * 1024          # 25 MB per file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Socket connection established'})


# ---------- helpers ---------------------------------------------------------

def allowed_file(fname: str) -> bool:
    return Path(fname).suffix.lower() in ALLOWED_EXT

def new_conv_folder() -> Path:
    cid = uuid.uuid4().hex[:16]
    p = UPLOAD_ROOT / cid
    p.mkdir(parents=True, exist_ok=True)
    return cid, p

def save_metadata(folder: Path, meta: dict) -> None:
    (folder / "index.json").write_text(json.dumps(meta, indent=2))

def map_state(action_id: str) -> tuple[int, int]:
    """
    Maps the action ID to a human-readable state.
    """
    action_states = {
        "uploading": 1,
        "splitting": 2,
        "scoring": 3,
        "checking grammar": 4,
        "finished": 5,
        "error": 0
    }
    
    current_action = action_states.get(action_id, 0)
    total_actions = len(action_states) - 1
    
    return current_action, total_actions

# ---------- routes ----------------------------------------------------------

@app.route("/")
def home():
    return {"message": "You are alive on speaklarity server!"}


@app.route("/upload-conversation", methods=["POST"])
def upload_conversation():
    # FIXME: temporarily disable this endpoint
    # return jsonify({"message": "This endpoint is not serving now :)"}), 201

    file: FileStorage | None = request.files.get("file")
    if not file:
        abort(400, "No file part in the request")
    if not file.filename:
        abort(400, "No selected file")
    if not allowed_file(file.filename):
        abort(400, "Only .wav files are accepted")

    cid, folder = new_conv_folder()
    original = secure_filename(file.filename)
    target   = folder / f"conversation_{cid}{Path(original).suffix.lower()}"

    # stream to disk
    save_audio_to_wav(file, str(target))

    # robust: hash after save (streaming would be better for > MAX_BYTES)
    h = hashlib.sha256(target.read_bytes()).hexdigest()

    # Save metadata in index.json inside the conversation_id folder
    index_path = folder / "index.json"
    metadata: dict[str, str] = {
        "conversation_id": cid,
        "filename": original,
        "sha256": h,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "action": "uploading...",
    }

    save_metadata(folder, metadata)

    socketio.emit("status", {
        "conversation_id": cid,
        "action": "uploading",
        "message": "File uploaded successfully, starting processing..."
    })

    # Run pipeline in a background thread so it doesn't block the request
    threading.Thread(target=pipeline, args=(cid,socketio), daemon=True).start()

    return metadata, 201


@app.route("/list-audio", methods=["GET"])
def list_audio():
    out = []
    for idx, child in enumerate(UPLOAD_ROOT.iterdir()):
        meta_file = child / "index.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            # summary = save_metadata_from_json(meta.get("sentence_text", ""))
            summary = meta.get("summary", "")
            action = meta.get("action", "error")
            current_action, total_actions = map_state(action) 
            out.append({"action": action, "total_actions": total_actions, "summary": summary,
                        "actions_done": current_action, "id": meta["conversation_id"],})
    return out

@app.route("/delete-conversation/<conv_id>", methods=["DELETE"])
def delete_conversation(conv_id: str):
    folder = UPLOAD_ROOT / conv_id
    if not folder.exists():
        abort(404, "Conversation ID not found")
    
    # Remove the entire conversation folder and its contents recursively
    shutil.rmtree(folder)

    socketio.emit("status", {
        "conversation_id": conv_id,
        "action": "deleted",
        "message": f"Conversation {conv_id} deleted successfully."
    })

    return jsonify({"message": "Conversation deleted successfully"}), 200

@app.route("/download-conversation/<conv_id>", methods=["GET"])
def download_conversation(conv_id: str):
    folder = UPLOAD_ROOT / conv_id
    if not folder.exists():
        abort(404, "Conversation ID not found")

    meta = json.loads((folder / "index.json").read_text())
    stored_file = None
    # Try to find the actual stored file in the folder
    for f in folder.iterdir():
        if f.is_file() and f.name.startswith("conversation_"):
            stored_file = f.name
            break
    if not stored_file:
        abort(404, "Audio file not found")
    return send_from_directory(folder, stored_file, as_attachment=True, mimetype="audio/wav")

@app.route("/native-reference/<conv_id>/<sentence_id>", methods=["GET"])
def get_native_reference(conv_id: str, sentence_id: int):
    """
    Serve the native reference audio for a specific sentence in a conversation.
    
    Args:
        conv_id (str): Unique identifier for the conversation.
        sentence_id (int): Index of the sentence to retrieve the native reference for.
    
    Returns:
        Response: The native reference audio file if found, 404 otherwise.
    """
    folder = UPLOAD_ROOT / conv_id / "sentences"
    if not folder.exists():
        abort(404, "Conversation ID not found")
    
    native_ref_file = folder / f"sentence_{sentence_id}_native.wav"
    if not native_ref_file.exists():
        abort(404, "Native reference audio not found")
    
    return send_from_directory(folder, native_ref_file.name, as_attachment=True, mimetype="audio/wav")

@app.route("/conv/<conv_id>", methods=["GET"])
def get_conversation(conv_id: str):
    folder = UPLOAD_ROOT / conv_id
    if not folder.exists():
        abort(404, "Conversation ID not found")

    meta = json.loads((folder / "index.json").read_text())

    return jsonify(meta)

# ---------- main ------------------------------------------------------------

if __name__ == "__main__":
    UPLOAD_ROOT.mkdir(exist_ok=True)
    # socketio.run(app, host="0.0.0.0", port=9000, debug=False)
    socketio.run(app, port=9000, debug=False, allow_unsafe_werkzeug=True)
