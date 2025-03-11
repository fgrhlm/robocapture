#!/bin/bash
set -e

function download_from_urls() {
    for url in "$@"
    do
        wget -nc "${url}"
    done
}

function main() {
    local dl_root="models"
    mkdir -pv "${dl_root}" && cd "${dl_root}"

    # YOLO 11n, 10n, 6n, 8n, 5s, 9t
    declare -a yolo=(
        "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt"
        "https://github.com/THU-MIG/yolov10/releases/download/v1.1/yolov10n.pt"
        "https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-t-converted.pt"
        "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt"
        "https://github.com/meituan/YOLOv6/releases/download/0.4.0/yolov6n.pt"
        "https://github.com/meituan/YOLOv6/releases/download/0.4.0/yolov6lite_s.pt"
        "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt"
    )
    download_from_urls "${yolo[@]}"

    # Yunet
    declare -a yunet=(
        "https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
        "https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/face_detection_yunet/face_detection_yunet_2023mar_int8.onnx"
        "https://github.com/opencv/opencv_zoo/raw/refs/heads/main/models/face_detection_yunet/face_detection_yunet_2023mar_int8bq.onnx"
    )
    download_from_urls "${yunet[@]}"

    # Whisper
    python -c "import whisper; whisper.load_model('tiny', download_root='.')"
    python -c "import whisper; whisper.load_model('tiny.en', download_root='.')"
}

main
