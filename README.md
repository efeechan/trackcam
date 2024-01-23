# User Tracking Webcam for Video Conferencing

This project is a Python-based application developed to enhance video conferencing experiences by enabling real-time user tracking. It integrates the YOLO (You Only Look Once) object detection model within a client-server architecture, focusing on webcam streams.

### Core Components
- Object Detection: Utilizes YOLOv8 for its precision in real-time object identification and localization.
- Dynamic Frame Adjustment: A key feature that keeps the subject centered in the webcam feed, adapting to movement.
- Client-Server Setup: Divided into server (server.py) and client (client.py) components, handling model processing and video capture respectively.

### Technologies Used
- YOLO (You Only Look Once): For efficient and accurate object detection.
- Python: Offers flexibility and is supported by extensive libraries.
- OpenCV: Manages webcam capture, image processing, and display.

### Objectives and Achievements
- The system effectively maintains the subject's visibility with precision and low latency, particularly beneficial in video conferencing scenarios.
- It demonstrates the practical application of advanced computer vision techniques in real-world scenarios.

## How to Use
### Setting Up the Environment
- Clone the Repository: If the project is hosted on a GitHub repository, clone it to your local machine using git clone [repository URL]. This step will download all the necessary files, including the client and server scripts (client.py and server.py).
- Install Required Libraries: Use the requirements.txt file to install necessary libraries. You can do this by running the command pip install -r requirements.txt in your terminal or command prompt. This file includes all the external libraries such as YOLO, OpenCV, NumPy, and others essential for the application​​.

### Running the Application
- Start the Server: Navigate to the directory where server.py is located and run it using the command python server.py. This initiates the server-side process, which includes loading the YOLO model and setting up socket communication.

- Launch the Client: In a separate terminal, navigate to the directory containing client.py and execute it with python client.py. This action starts the client-side process, involving webcam capture and transmission of frames for analysis.

- Using the Application: With both the client and server running, the system will begin processing the webcam feed in real-time. The YOLO model integrated on the server side will detect and track objects (or users) in the webcam stream. The client side dynamically adjusts the frame to keep the subject centered.

- Interacting with the System: Observe the system's real-time tracking and frame adjustment capabilities. The application is designed to enhance video conferencing by keeping the subject in focus, adapting to movements and changes in the scene.

## Troubleshooting
- Ensure all dependencies are correctly installed as per the requirements.txt file.
- Check for proper network configurations and settings, as the client and server communicate over a network.
- Verify that your webcam is functioning correctly for the client application to capture video feed.
