from werkzeug.datastructures.file_storage import FileStorage
from flask import Flask, jsonify, send_from_directory, request, abort
from werkzeug.utils import secure_filename
import hashlib, json, os, uuid
from pathlib import Path
from datetime import datetime, timezone
import time

from process import pipeline
from util import save_audio_to_wav

UPLOAD_ROOT = Path("data")
ALLOWED_EXT = {".wav"}
MAX_BYTES   = 25 * 1024 * 1024          # 25 MB per file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES


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

# ---------- routes ----------------------------------------------------------

@app.route("/")
def home():
    return {"message": "You are alive on speaklarity server!"}


@app.route("/upload-conversation", methods=["POST"])
def upload_conversation():
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
    metadata = {
        "conversation_id": cid,
        "filename": original,
        "sha256": h,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }

    save_metadata(folder, metadata)

    pipeline(cid)  # process the audio file, cid: conversation ID

    return metadata, 201


@app.route("/list-audio", methods=["GET"])
def list_audio():
    out = []
    for idx, child in enumerate(UPLOAD_ROOT.iterdir()):
        meta_file = child / "index.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            out.append({"audio_id": idx, **meta})
    return out


@app.route("/raw/<conv_id>")
def get_raw(conv_id: str):
    folder = UPLOAD_ROOT / conv_id
    if not folder.exists():
        abort(404, "conversation id not found")

    meta = json.loads((folder / "index.json").read_text())
    return send_from_directory(folder, meta["stored_as"], mimetype="audio/wav")


# ----------------- accent / grammar demo stubs ------------------------------

@app.route("/accent-check/<conv_id>")
def accent_check(conv_id):
    # TODO: real analysis; here’s a placeholder
    return [
        {"start": 0.5, "end": 1.3, "accent_id": 0},
        {"start": 2.0, "end": 2.7, "accent_id": 1},
    ]


@app.route("/accent/<conv_id>/<int:accent_id>")
def correct_accent(conv_id, accent_id):
    demo = {(0, 0): "accent_demo_0.wav"}  # look up your real file…
    key = (int(conv_id, 16) % 2, accent_id)  # arbitrary mapping example
    fname = demo.get(key)
    if not fname:
        abort(404)
    accent_dir = Path("assets/accents")
    return send_from_directory(str(accent_dir), fname, mimetype="audio/wav")


@app.route("/grammar-check/<conv_id>")
def grammar_check(conv_id):
    return [
        {"start": 1.0, "end": 2.0, "grammar_id": 0},
        {"start": 3.0, "end": 4.0, "grammar_id": 1},
    ]


@app.route("/grammar/<int:grammar_id>")
def correct_grammar(grammar_id):
    data = {
        0: {"sentence": "This is the correct sentence one.", "audio": "g1.wav"},
        1: {"sentence": "This is the correct sentence two.", "audio": "g2.wav"},
    }
    item = data.get(grammar_id)
    if not item:
        abort(404)
    return item    # just JSON; add `/grammar/<id>/audio` to send file


# ---------- main ------------------------------------------------------------

if __name__ == "__main__":
    UPLOAD_ROOT.mkdir(exist_ok=True)
    app.run(host="0.0.0.0", port=9000, debug=False)
