import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """Calculate angle between three points."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def calculate_angle_x_axis(a, b):
    """Calculate angle between two points and x-axis."""
    a = np.array(a)
    b = np.array(b)
    radians = np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def live_deadlift_tracking():
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    counter = 0
    stage = None
    progress_percentage = 0

    progress_bar = {
        'x': 50,
        'y_start': 150,
        'height': 400,
        'width': 20
    }

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame.")
                break

            # Process the frame
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates for deadlift tracking
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hips = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                # Calculate angles
                hip_angle = calculate_angle(shoulder, hips, knee)
                knee_angle = calculate_angle(hips, knee, ankle)
                back_angle = calculate_angle_x_axis(shoulder, hips)

                # Deadlift stage detection
                if hip_angle < 150 and stage != "Down":
                    stage = "Down"
                elif 150 <= hip_angle < 160 and (stage == "Down" or stage == "Lockout"):
                    stage = "Up"
                elif 160 <= hip_angle <= 180 and stage == "Up":
                    stage = "Lockout"
                    counter += 1

                # Calculate progress percentage
                if stage == "Down" and hip_angle < 150:
                    progress_percentage = 0
                elif stage == "Up" and 150 <= hip_angle < 160:
                    progress_percentage = int(((hip_angle - 150) / (160 - 150)) * 50)
                elif stage == "Lockout" and 160 <= hip_angle <= 180:
                    progress_percentage = 50 + int(((hip_angle - 160) / (180 - 160)) * 50)

                # Draw angle labels
                cv2.putText(image, f'Hip: {int(hip_angle)}',
                            tuple(np.multiply(hips, [image.shape[1], image.shape[0]]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f'Knee: {int(knee_angle)}',
                            tuple(np.multiply(knee, [image.shape[1], image.shape[0]]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(image, f'Back: {int(back_angle)}',
                            tuple(np.multiply(shoulder, [image.shape[1], image.shape[0]]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            except Exception as e:
                print(f"Error processing frame: {str(e)}")
                pass

            # Draw overlay and stats
            overlay = image.copy()
            cv2.rectangle(overlay, (0, 0), (225, 100), (245, 117, 16), -1)
            cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)

            # Add stats
            cv2.putText(image, 'REPS', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, str(counter), (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3, cv2.LINE_AA)
            cv2.putText(image, 'STAGE:', (10, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, stage if stage else "", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3, cv2.LINE_AA)

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

            # Add percentage text
            cv2.putText(image, f'{progress_percentage}%',
                        (progress_bar['x'] - 20, progress_bar['y_start'] + progress_bar['height'] + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

            # Draw pose landmarks
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            cv2.imshow('Deadlift Tracker', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    live_deadlift_tracking()
