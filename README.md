# Rip current detection

Rip currents are narrow, fast channels of water that pull swimmers away from shore. They are hard to spot from the beach, and they kill people who never intended to swim out. This project detects them visually, so a drone, a smartphone, or other edge hardware can mark the water in front of a person before they enter it.

A YOLOv8s instance-segmentation model, trained on the [RipVIS](https://ripvis.ai) beach-video dataset, draws a mask over rip current in a shoreline photo. The live demo uploads a frame and returns the annotated image.

## Why it matters

NOAA Storm Events Database, 2010 through June 2026:

- Rip currents are the second-deadliest hydrometeorological hazard by direct deaths (929), behind flash floods.
- Among the ten deadliest of those hazards, rip currents have the highest number of direct deaths per reported incident.

The chart scripts in this repo turn that export into the figures used in the pitch.

## What is in this repo

| Path | Role |
| --- | --- |
| `bargraphtop10.py` | Bar chart of direct deaths for the top 10 hydrometeorological hazards. Rip current is highlighted. |
| `ratiotop10.py` | Deaths per 100 reported incidents for those same hazards. |
| `train-seg.py` | Trains a YOLOv8s segmentation model on RipVIS. |
| `yolo_web_app/` | Flask demo: upload a coastal photo, get the mask back. |

```
bargraphtop10.py
ratiotop10.py
train-seg.py
yolo_web_app/
  app.py
  templates/index.html
  static/
```

## Setup

Python 3.10 or newer. From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install ultralytics flask opencv-python numpy matplotlib pandas
```

## Visuals

`bargraphtop10.py` has the death totals baked in. It writes `top10_marine_deaths.png`.

```bash
python bargraphtop10.py
```

`ratiotop10.py` reads `countdeath.csv` in the working directory. The file needs three columns: event type, direct deaths, and incident count (a NOAA-style export of `event_type`, `sum(deaths_direct)`, `count(*)`). It writes `incident_death_ratio.png`.

```bash
python ratiotop10.py
```

## Training

`train-seg.py` fine-tunes YOLOv8s segmentation for 300 epochs at 640 px on GPU 0, starting from `segment-run-1.pt` in the working directory. Checkpoints land in `runs/segment-run-4/yolov8s-ripvis/`.

Place the RipVIS YOLO split next to the script:

```
datasets/ripvis/
  data.yaml
  train/images/
  train/labels/
  val/images/
  val/labels/
  test/images/
  test/labels/
```

`data.yaml` should point `train`, `val`, and `test` at those image folders and name class `0` as `rip_current`. Then:

```bash
python train-seg.py
```

RipVIS is the CVPR 2025 beach-monitoring benchmark (184 videos, polygon masks on frames that contain rip current). Use the authors' manual train/val/test split so frames from the same video do not leak across sets. The dataset is [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/); see the [RipVIS dataset card](https://huggingface.co/datasets/Irikos/RipVIS) before redistributing it.

## Live demo

The demo loads a trained checkpoint, accepts a JPEG, PNG, WebP, or BMP up to 20 MB, and returns the mask, class, and confidence.

Point `WEIGHTS` in `yolo_web_app/app.py` at your checkpoint (it is currently an absolute path on the training machine), then from the repo root:

```bash
python yolo_web_app/app.py
```

Open [http://127.0.0.1:5050](http://127.0.0.1:5050), drop a shoreline photo, and the page shows the source next to the segmentation.

The same weights are what you would run on a drone, a phone, or another edge device: one frame in, a rip-current mask out.

## Citation

If you use RipVIS, cite Dumitriu et al., *RipVIS: Rip Currents Video Instance Segmentation Benchmark for Beach Monitoring and Safety*, CVPR 2025.
