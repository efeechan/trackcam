# server.py

from ultralytics import YOLO
import cv2
import math
import socket
import pickle
import struct
import sys
import traceback
import threading

# import torch

# model
# model = YOLO("yolo-Weights/yolov8n.pt")

# Export the model
# model.export(format="openvino")  # creates 'yolov8n_openvino_model/'

# Load the exported OpenVINO model
# torch.cuda.set_device(0)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = YOLO("yolo-weights/yolov8n_openvino_model/", task="detect")
# model.to(device=device)

# Object classes
classNames = [
    "person",
    "bicycle",
    "car",
    "motorbike",
    "aeroplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "sofa",
    "pottedplant",
    "bed",
    "diningtable",
    "toilet",
    "tvmonitor",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]

# create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set TCP_NODELAY option
server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

server_socket.bind(("0.0.0.0", 0))
server_socket.listen(5)

# Get the dynamically assigned port
host, port = server_socket.getsockname()
print(f"Server listening on {host}:{port}")


def handle_client(client_socket):
    try:
        while True:
            # Receive frame data from the client
            data = b""
            payload_size = struct.calcsize("L")

            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    break
                data += packet

            if not data:
                break  # Break out of the loop if no data is received

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("I", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Unpack frame data and resize it back to the original resolution
            resized_frame = pickle.loads(frame_data)
            original_frame = cv2.resize(
                resized_frame, (1280, 720)
            )  # Adjust to the original resolution

            # Process the received frame using the YOLO model
            results = model(original_frame, stream=True)

            # Process results and filter for "person" class
            biggest_person_info = None

            for r in results:
                boxes = r.boxes

                for box in boxes:
                    cls = int(box.cls[0])

                    # Filter for "person" class
                    if classNames[cls] == "person":
                        # bounding box
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        # confidence
                        confidence = math.ceil((box.conf[0] * 100)) / 100

                        # object details
                        box_info = {
                            "class": classNames[cls],
                            "confidence": confidence,
                            "coordinates": (x1, y1, x2, y2),
                        }

                        if biggest_person_info is None or (x2 - x1) * (y2 - y1) > (
                            biggest_person_info["coordinates"][2]
                            - biggest_person_info["coordinates"][0]
                        ) * (
                            biggest_person_info["coordinates"][3]
                            - biggest_person_info["coordinates"][1]
                        ):
                            biggest_person_info = box_info

            # Send processed results back to the client if a biggest person is found
            if biggest_person_info:
                data = pickle.dumps([biggest_person_info])
                client_socket.sendall(data)

    except (socket.error, ConnectionResetError):
        print("Client disconnected.")
    except Exception as e:
        print("Error:", e)
        traceback.print_exc(file=sys.stdout)
    finally:
        # Close the client socket
        client_socket.close()


while True:
    # Accept incoming client connection
    client_socket, addr = server_socket.accept()
    print("Connection from", addr)

    # Create a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()

# Close the server socket
server_socket.close()
cv2.destroyAllWindows()
