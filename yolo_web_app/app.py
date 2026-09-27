#!/usr/bin/env python3
"""Upload an image, run RipVIS YOLO segmentation, and return the annotated frame.

From the repo root:

    .venv/bin/python yolo_web_app/app.py

Then open http://127.0.0.1:5050
"""

from __future__ import annotations

import base64
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
WEIGHTS = Path("/home/rchilka/storage/projects/cdc_hackathon_storm/segment-run-1.pt")

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_BYTES = 20 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_BYTES
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

_model: YOLO | None = None
_model_lock = threading.Lock()
_predict_lock = threading.Lock()


def get_model() -> YOLO:
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                if not WEIGHTS.is_file():
                    raise FileNotFoundError(f"weights not found: {WEIGHTS}")
                _model = YOLO(str(WEIGHTS))
    return _model


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/segment")
def segment():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        return jsonify(error="Choose an image to segment."), 400

    content_type = (upload.mimetype or "").split(";")[0].strip().lower()
    suffix = Path(upload.filename).suffix.lower()
    if content_type not in ALLOWED_TYPES and suffix not in ALLOWED_SUFFIXES:
        return jsonify(error="Use a JPEG, PNG, WebP, or BMP image."), 400

    raw = upload.read()
    if not raw:
        return jsonify(error="That file is empty."), 400

    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return jsonify(error="Could not read that image."), 400

    started = time.perf_counter()
    model = get_model()
    with _predict_lock:
        results = model.predict(
            source=image,
            imgsz=640,
            conf=0.25,
            retina_masks=True,
            verbose=False,
        )
    elapsed_ms = round((time.perf_counter() - started) * 1000)

    result = results[0]
    annotated = result.plot()
    ok, encoded = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not ok:
        return jsonify(error="Could not encode the result."), 500

    detections = []
    if result.boxes is not None:
        names = result.names or {}
        for box in result.boxes:
            class_id = int(box.cls[0])
            detections.append(
                {
                    "class": names.get(class_id, str(class_id)),
                    "confidence": round(float(box.conf[0]), 3),
                }
            )
    detections.sort(key=lambda item: item["confidence"], reverse=True)

    height, width = annotated.shape[:2]
    payload = base64.b64encode(encoded.tobytes()).decode("ascii")
    return jsonify(
        image=f"data:image/jpeg;base64,{payload}",
        width=int(width),
        height=int(height),
        elapsed_ms=elapsed_ms,
        count=len(detections),
        detections=detections,
    )


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="Image must be 20 MB or smaller."), 413


if __name__ == "__main__":
    print(f"Loading {WEIGHTS}", flush=True)
    get_model()
    print("RipVIS segmenter at http://127.0.0.1:5050", flush=True)
    app.run(host="127.0.0.1", port=5050, debug=False, threaded=True)
