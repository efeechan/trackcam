# client.py

import cv2
import socket
import pickle
import struct
import threading
import time
import math
import pyvirtualcam

# Constants
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720
VISIBLE_WIDTH = 960
VISIBLE_HEIGHT = 540
BUFFER_SIZE = 4096
MOVE_STEP = 2
MOVE_INTERVAL = 0.001

# Global variables for thread communication
visible_frame_x, visible_frame_y = 640, 360
lock = threading.Lock()

# Load the placeholder image
placeholder_image = cv2.imread(
    "C:/Users/eyilmazdemir/Desktop/final/final/placeholder.jpg"
)  # Replace with your image file
placeholder_image = cv2.flip(placeholder_image, 1)


def initialize_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

    if not cap.isOpened():
        print("Failed to open camera. Exiting.")
        return None

    return cap


def initialize_virtual_camera():
    return pyvirtualcam.Camera(width=VISIBLE_WIDTH, height=VISIBLE_HEIGHT, fps=30)


def update_visible_frame_position_dynamic(target_x, target_y):
    global visible_frame_x, visible_frame_y
    with lock:
        # Calculate the distance between current position and target position
        distance = math.sqrt(
            (target_x - visible_frame_x) ** 2 + (target_y - visible_frame_y) ** 2
        )

        # Adjust the interpolation factor based on distance
        interpolation_factor = min(
            1.0, distance / 100.0
        )  # You can adjust the divisor for sensitivity

        # Use adjusted interpolation factor for smoother movement
        visible_frame_x += int((target_x - visible_frame_x) * interpolation_factor)
        visible_frame_y += int((target_y - visible_frame_y) * interpolation_factor)

        # Ensure the visible frame stays within the image boundaries
        visible_frame_x = max(0, min(CAPTURE_WIDTH - VISIBLE_WIDTH, visible_frame_x))
        visible_frame_y = max(0, min(CAPTURE_HEIGHT - VISIBLE_HEIGHT, visible_frame_y))


def calculate_visible_frame_position(human_coordinates):
    x1, y1, x2, y2 = human_coordinates
    human_center_x = (x1 + x2) // 2
    human_center_y = (y1 + y2) // 2

    visible_frame_x = max(0, human_center_x - VISIBLE_WIDTH // 2)
    visible_frame_y = max(0, human_center_y - VISIBLE_HEIGHT // 2)

    if visible_frame_x + VISIBLE_WIDTH > CAPTURE_WIDTH:
        visible_frame_x = CAPTURE_WIDTH - VISIBLE_WIDTH

    if visible_frame_y + VISIBLE_HEIGHT > CAPTURE_HEIGHT:
        visible_frame_y = CAPTURE_HEIGHT - VISIBLE_HEIGHT

    return visible_frame_x, visible_frame_y


def receive_and_display_results(client_socket, virtual_cam):
    cap = initialize_camera()

    if cap is None:
        client_socket.close()
        return

    while True:
        success, img = cap.read()

        # Switch from BGR to RGB format
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Flip the frame horizontally
        # img = cv2.flip(img, 1)

        if not success:
            print("Failed to capture frame")
            break

        resized_frame = cv2.resize(img, (VISIBLE_WIDTH, VISIBLE_HEIGHT))

        data = pickle.dumps(resized_frame)
        client_socket.sendall(struct.pack("L", len(data)) + data)

        # Set a timeout for receiving processed results (adjust the timeout value as needed)
        client_socket.settimeout(1.0)
        try:
            data = client_socket.recv(BUFFER_SIZE)
            processed_results = pickle.loads(data)
        except socket.timeout:
            # Handle the case where no data is received within the timeout
            print("Timeout: No processed results received.")
            processed_results = None

        if not data:
            break

        if processed_results and processed_results[0]:
            human_coordinates = processed_results[0]["coordinates"]
            target_x, target_y = calculate_visible_frame_position(human_coordinates)
            update_visible_frame_position_dynamic(target_x, target_y)
        else:
            # Use the last known position if no detection
            with lock:
                target_x, target_y = visible_frame_x, visible_frame_y

        # Display the visible frame
        with lock:
            visible_frame = img[
                target_y : target_y + VISIBLE_HEIGHT,
                target_x : target_x + VISIBLE_WIDTH,
            ]

            # If no detection, use the placeholder image
            if processed_results is None:
                visible_frame = placeholder_image

        cv2.imshow("Visible Frame", visible_frame)

        # Send the visible frame to the virtual camera
        virtual_cam.send(visible_frame)

        if cv2.waitKey(1) == ord("q"):  # Reduce the delay here (1 millisecond)
            break

        # Only sleep if not in a timeout state
        if processed_results is not None:
            time.sleep(MOVE_INTERVAL)

    cap.release()
    client_socket.close()
    cv2.destroyAllWindows()


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 14943))

    try:
        # Initialize the virtual camera
        virtual_cam = initialize_virtual_camera()

        # Create a thread for receiving and displaying results
        receive_thread = threading.Thread(
            target=receive_and_display_results,
            args=(client_socket, virtual_cam),
        )
        receive_thread.start()

        # Your main thread can perform other tasks if needed

        # Wait for the receive_thread to finish
        receive_thread.join()

    except KeyboardInterrupt:
        pass
    finally:
        # Close the virtual camera
        virtual_cam.close()


if __name__ == "__main__":
    main()
