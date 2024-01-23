# User Tracking Webcam for Video Conferencing

This project is a Python-based application developed to enhance video conferencing experiences by enabling real-time user tracking. It integrates the YOLO (You Only Look Once) object detection model within a client-server architecture, focusing on webcam streams.

## Core Components
- Object Detection: Utilizes YOLOv8 for its precision in real-time object identification and localization.
- Dynamic Frame Adjustment: A key feature that keeps the subject centered in the webcam feed, adapting to movement.
- Client-Server Setup: Divided into server (server.py) and client (client.py) components, handling model processing and video capture respectively.

## Technologies Used
- YOLO (You Only Look Once): For efficient and accurate object detection.
- Python: Offers flexibility and is supported by extensive libraries.
- OpenCV: Manages webcam capture, image processing, and display.

## Objectives and Achievements
- The system effectively maintains the subject's visibility with precision and low latency, particularly beneficial in video conferencing scenarios.
- It demonstrates the practical application of advanced computer vision techniques in real-world scenarios.
