import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def live_bicep_tracking():
    """Processes live webcam feed to track bicep curls."""
    counter = 0
    stage = None

    # Progress bar parameters
    progress_bar = {
        'x': 30,
        'y_start': 80,
        'height': 200,
        'width': 10
    }

    font_scale = {
        'stats': 0.4,
        'counts': 0.5,
        'progress': 0.4
    }

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise ValueError("Error: Could not access the webcam")

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read from the webcam")
                break

            # Flip the frame horizontally for natural mirroring
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            # Revert image back to BGR for OpenCV
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates for bicep curl tracking
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Calculate curl angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Calculate progress for bicep curl
                progress_percentage = 0
                if angle >= 140:  # Adjusted for bicep curl starting position
                    progress_percentage = 0
                elif angle <= 40:  # Adjusted for bicep curl end position
                    progress_percentage = 100
                else:
                    progress_percentage = ((140 - angle) / (140 - 40)) * 100
                    progress_percentage = max(0, min(100, progress_percentage))

                # Count reps with bicep curl specific angles
                if angle > 140:
                    stage = "down"
                if angle < 40 and stage == 'down':
                    stage = "up"
                    counter += 1

            except:
                pass

            # Draw overlay and stats
            overlay = image.copy()
            cv2.rectangle(overlay, (0, 0), (180, 60), (245, 117, 16), -1)
            cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)

            # Add stats
            cv2.putText(image, 'REPS', (10, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale['stats'], (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), (10, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale['counts'], (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(image, 'STAGE', (10, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale['stats'], (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(image, stage if stage else "", (10, 58),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale['counts'], (255, 255, 255), 1, cv2.LINE_AA)

            # Draw progress bar
            filled_height = int((progress_percentage / 100) * progress_bar['height'])
            cv2.rectangle(image,
                          (progress_bar['x'], progress_bar['y_start']),
                          (progress_bar['x'] + progress_bar['width'],
                           progress_bar['y_start'] + progress_bar['height']),
                          (200, 200, 200), -1)
            cv2.rectangle(image,
                          (progress_bar['x'],
                           progress_bar['y_start'] + progress_bar['height'] - filled_height),
                          (progress_bar['x'] + progress_bar['width'],
                           progress_bar['y_start'] + progress_bar['height']),
                          (255, 0, 255), -1)

            # Draw pose landmarks
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            # Display the live feed
            cv2.imshow('Bicep Curl Tracker', image)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    live_bicep_tracking()
