"""Train a YOLOv8s instance-segmentation model on the RipVIS dataset."""

from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "datasets" / "ripvis" / "data.yaml"


def main() -> None:
    model = YOLO("segment-run-1.pt")
    model.train(
        data=str(DATA),
        epochs=300,
        imgsz=640,
        batch=-1,
        device=0,
        project=str(ROOT / "runs" / "segment-run-4"),
        name="yolov8s-ripvis",
        save=True
    )


if __name__ == "__main__":
    main()
