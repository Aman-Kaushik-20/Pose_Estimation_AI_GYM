import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os
from datetime import datetime

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def process_video(input_path):
    """
    Process the deadlift video and save outputs to temporary files.
    Returns tuple of (processed_video_path, log_path)
    """
    # Create temporary files
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
    
    try:
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video file at {input_path}")
        
        # Get video properties
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Initialize video writer with temporary file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video.name, fourcc, fps, (frame_width, frame_height))
        
        counter = 0 
        stage = None
        frame_count = 0
        progress_percentage = 0
        
        # Progress bar parameters
        progress_bar = {
            'x': 50,
            'y_start': 150,
            'height': 400,
            'width': 20
        }
        
        with open(temp_log.name, 'w') as log_file:
            log_file.write(f"Processing started at: {datetime.now()}\n")
            
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                    
                    frame_count += 1
                    
                    # Process frame
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
                            
                            #log_file.write(f"Rep {counter} detected at frame {frame_count}\n")
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
                                  tuple(np.multiply(hips, [frame_width, frame_height]).astype(int)), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(image, f'Knee: {int(knee_angle)}', 
                                  tuple(np.multiply(knee, [frame_width, frame_height]).astype(int)), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(image, f'Back: {int(back_angle)}', 
                                  tuple(np.multiply(shoulder, [frame_width, frame_height]).astype(int)), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                        
                    except Exception as e:
                        log_file.write(f"Error processing frame {frame_count}: {str(e)}\n")
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
                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                    )
                    
                    out.write(image)
                
                log_file.write(f"\nProcessing completed at: {datetime.now()}\n")
                log_file.write(f"Total frames processed: {frame_count}\n")
                log_file.write(f"Total reps counted: {counter}\n")
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        return temp_video.name, temp_log.name
        
    except Exception as e:
        # Clean up temporary files if there's an error
        try:
            os.unlink(temp_video.name)
            os.unlink(temp_log.name)
        except:
            pass
        raise e

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360-angle
    return angle

def calculate_angle_x_axis(a, b):
    """Calculate angle between two points and x-axis"""
    a = np.array(a)
    b = np.array(b)
    radians = np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360-angle
    return angle