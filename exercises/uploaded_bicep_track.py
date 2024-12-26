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
    Process the bicep curl video and save outputs to temporary files.
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
        
        # Initialize video writer with temporary file
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video.name, fourcc, fps, (frame_width, frame_height))
        
        counter = 0 
        stage = None
        frame_count = 0
        progress_percentage = 0
        
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
                            log_file.write(f"Rep {counter} completed at frame {frame_count}\n")
                        
                        # Log the angle for form analysis
                        if frame_count % 30 == 0:  # Log every 30 frames
                            log_file.write(f"Frame {frame_count}: Curl angle = {angle:.1f}°\n")
                        
                    except Exception as e:
                        log_file.write(f"Frame {frame_count}: Failed to detect pose landmarks\n")
                        continue
                    
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
                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                    )
                    
                    out.write(image)
                
                log_file.write(f"\nProcessing completed at: {datetime.now()}\n")
                log_file.write(f"Total frames processed: {frame_count}\n")
                log_file.write(f"Total reps counted: {counter}\n")
                
                # Add form analysis summary
                if counter > 0:
                    log_file.write("\nForm Analysis Summary:\n")
                    log_file.write("- Proper bicep curl range: 40° to 140°\n")
                    log_file.write(f"- Average frames per rep: {frame_count/counter:.1f}\n")
        
        cap.release()
        out.release()
        
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