# File structure:
# /gym_tracker/
#   ├── app.py
#   ├── exercises/
#   │   ├── __init__.py
#   │   ├── pushup_processor.py
#   │   ├── deadlift_processor.py
#   │   └── bicep_processor.py

# exercises/__init__.py
# Empty file to make the directory a Python package

# exercises/pushup_processor.py
def process_video(input_path, output_dir=None):
    # Your pushup video processing implementation
    pass

def live_process_video():
    # Your pushup live processing implementation
    pass

# exercises/deadlift_processor.py
def process_video(input_path, output_dir=None):
    # Your deadlift video processing implementation
    pass

def live_process_video():
    # Your deadlift live processing implementation
    pass

# exercises/bicep_processor.py
def process_video(input_path, output_dir=None):
    # Your bicep curl video processing implementation
    pass

def live_process_video():
    # Your bicep curl live processing implementation
    pass

# app.py
import streamlit as st
from PIL import Image
import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime
import tempfile
from pathlib import Path
import subprocess
# Import exercise processors
from exercises.uploaded_pushup_track import process_video as pushup_process_video
from exercises.uploaded_deadlift_track import process_video as deadlift_process_video
from exercises.uploaded_bicep_track import process_video as bicep_process_video
from exercises.live_pushup_track import live_pushup_tracking as pushup_live_track
from exercises.live_deadlift_track import live_deadlift_tracking as deadlift_live_track
from exercises.live_bicep_track import live_bicep_tracking as bicep_live_track



# Set page config
st.set_page_config(
    page_title="Fitness Form Tracker",
    page_icon="💪",
    layout="wide"
)

# Initialize session state variables
if 'current_page' not in st.session_state: 
    st.session_state.current_page = 'home'

def set_background():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: url("https://raw.githubusercontent.com/Aman-Kaushik-20/A_GYM_ASSISTANT/main/cyberpunk_01.jpeg");
            background-size: cover;
            background-position: center;
        }
        
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0);
        }
        
        /* Main title styles */
        h1 {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            background: rgba(0,0,0,0.6);
            padding: 20px;
            border-radius: 10px;
            font-size: 2.5rem !important;
        }

        /* Exercise title styles - matching main title */
        .exercise-title {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            background: rgba(0,0,0,0.6);
            padding: 20px;
            border-radius: 10px;
            font-size: 2.5rem !important;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* Instructions title style */
        .instructions-title {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            background: rgba(0,0,0,0.6);
            padding: 15px;
            border-radius: 8px;
            font-size: 1.8rem !important;
            margin-bottom: 1.5rem;
        }
        
        /* Exercise instructions container */
        .exercise-instructions {
            background: rgba(0,0,0,0.6);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        /* Instructions list style */
        .exercise-instructions ol {
            list-style-position: inside;
            padding-left: 0;
        }
        
        .exercise-instructions ol li {
            color: white !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
            padding: 10px 15px;
            margin: 8px 0;
            background: rgba(0,0,0,0.4);
            border-radius: 5px;
            font-size: 1.1rem;
            line-height: 1.5;
        }
        
        /* Note style */
        .camera-note {
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-left: 4px solid #ff00de;
            margin: 1rem 0;
            color: white;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
            font-weight: bold;
        }
        
        /* Hide the use_column_width warning messages */
        div[data-testid="stMarkdownContainer"] > div.stWarning {
            display: none !important;
        }
        
        /* Updated quote styles to match main title */
        .simple-quote {
            font-size: 2.5rem !important;
            font-weight: bold !important;
            text-align: center !important;
            margin: 2rem 0 !important;
            padding: 2rem !important;
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            background: rgba(0,0,0,0.6);
            border-radius: 10px;
            font-family: 'Arial Black', sans-serif !important;
        }
        
        /* Exercise card styles */
        .exercise-card {
            background: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            transition: transform 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
        }
        
        .exercise-card:hover {
            transform: translateY(-5px);
        }
        
        .exercise-image {
            width: 100%;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        /* Center button container */
        .button-container {
            width: 100%;
            display: flex;
            justify-content: center;
            margin-top: auto;
            padding: 1rem 0;
        }
        
        /* Button styles */
        .stButton button {
            background: linear-gradient(45deg, #ff00de, #00fff2) !important;
            border: none !important;
            color: white !important;
            padding: 0.8rem 2rem !important;
            font-weight: bold !important;
            border-radius: 5px !important;
            box-shadow: 0 0 15px rgba(0, 255, 242, 0.5) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 0 25px rgba(255, 0, 222, 0.7) !important;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background-color: rgba(0, 0, 0, 0.4);
            padding: 10px;
            border-radius: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            font-weight: bold;
            font-size: 1.1rem;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #ff00de !important;
        }

        .stTabs [aria-selected="true"] {
            color: #00fff2 !important;
        }

        /* Upload text styling */
        [data-testid="stFileUploadDropzone"] {
            background-color: rgba(0, 0, 0, 0.6) !important;
            border: 2px dashed rgba(255, 255, 255, 0.3) !important;
        }

        [data-testid="stFileUploadDropzone"] span {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
        }

        /* Upload limit text */
        [data-testid="stFileUploadDropzone"] small {
            color: rgba(255, 255, 255, 0.7) !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8) !important;
        }

        /* Browse files button */
        [data-testid="stFileUploadDropzone"] button {
            background: linear-gradient(45deg, #ff00de, #00fff2) !important;
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            border: none !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: bold !important;
            box-shadow: 0 0 15px rgba(0, 255, 242, 0.3) !important;
        }

        [data-testid="stFileUploadDropzone"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 0 25px rgba(255, 0, 222, 0.5) !important;
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )

def home_page():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    st.title("Welcome to Fitness Form Tracker 🏋️‍♂️")
    
    # Updated quote with smaller font size using custom CSS
    st.markdown("""
    <div class="simple-quote" style="font-size: 0.5rem !important;">
       " THE ONLY BAD WORKOUT IS THE ONE THAT DIDN'T HAPPEN "
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Enter Gym", key="enter_gym"):
            st.session_state.current_page = 'exercise_selection'

def exercise_selection_page():
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    st.title("Choose Your Exercise 💪")
    
    # Define image URLs
    images = {
        'pushup': "https://raw.githubusercontent.com/Aman-Kaushik-20/A_GYM_ASSISTANT/main/Pushup_04.jpeg",
        'deadlift': "https://raw.githubusercontent.com/Aman-Kaushik-20/A_GYM_ASSISTANT/main/deadlift_02.jpeg",
        'bicep': "https://raw.githubusercontent.com/Aman-Kaushik-20/A_GYM_ASSISTANT/main/bicep_04.jpeg"
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="exercise-card">', unsafe_allow_html=True)
        st.image(images['pushup'], use_container_width=True)
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("Push-ups", key="pushup_btn_selection"):  # Updated key
            st.session_state.current_page = 'pushup_page'
            st.session_state.selected_exercise = 'pushup'
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="exercise-card">', unsafe_allow_html=True)
        st.image(images['deadlift'], use_container_width=True)
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("Deadlifts", key="deadlift_btn_selection"):  # Updated key
            st.session_state.current_page = 'deadlift_page'
            st.session_state.selected_exercise = 'deadlift'
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="exercise-card">', unsafe_allow_html=True)
        st.image(images['bicep'], use_container_width=True)
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("Bicep Curls", key="bicep_btn_selection"):  # Updated key
            st.session_state.current_page = 'bicep_page'
            st.session_state.selected_exercise = 'bicep'
        st.markdown('</div></div>', unsafe_allow_html=True)

def handle_live_tracking(exercise_name):
    """
    Handle live video processing for the selected exercise.
    
    Args:
        exercise_name (str): Name of the exercise ('pushup', 'deadlift', or 'bicep')
    """
    # Import the appropriate live tracking module based on exercise
    try:
        if exercise_name == 'pushup':
            tracking_function = pushup_live_track
        elif exercise_name == 'deadlift':
            tracking_function = deadlift_live_track
        elif exercise_name == 'bicep':
            tracking_function = bicep_live_track
        else:
            st.error("Invalid exercise selected!")
            return
        
        # Create a placeholder for the video feed
        video_placeholder = st.empty()
        
        # Create status indicators
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        # Display initial status
        status_text.text("Initializing camera...")
        
        try:
            # Check if camera is available
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                st.error("Error: Could not access the webcam. Please make sure it's connected and not being used by another application.")
                cap.release()
                return
            cap.release()
            
            # Update status
            status_text.text(f"Starting {exercise_name} tracking. Press 'q' in the video window to stop.")
            
            # Start the live tracking
            tracking_function()
            
            # Clear status indicators after tracking ends
            status_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"Error during live tracking: {str(e)}")
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            
    except ImportError as e:
        st.error(f"Could not load the {exercise_name} tracking module: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    finally:
        # Ensure we always clean up
        cv2.destroyAllWindows()


def convert_video_to_h264(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vcodec", "libx264",
        "-acodec", "aac",
        output_path
    ]
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_processor(exercise_name):
    processors = {
        'pushup': uploaded_pushup_track,
        'deadlift': uploaded_deadlift_track,
        'bicep': uploaded_bicep_track
    }
    return processors.get(exercise_name)


def handle_video_upload(exercise_name, uploaded_file):
    if uploaded_file is not None:
        processors = {
            'pushup': pushup_process_video,
            'deadlift': deadlift_process_video,
            'bicep': bicep_process_video
        }
        processor = processors.get(exercise_name)
        
        if processor:
            temp_files = []
            try:
                # Create temporary files
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_input:
                    temp_input.write(uploaded_file.read())
                    temp_input_path = temp_input.name
                    temp_files.append(temp_input_path)
                
                # Create temp files for both original and processed videos
                temp_original_h264 = tempfile.mktemp(suffix='_original_h264.mp4')
                temp_files.append(temp_original_h264)
                
                # Show processing status
                status_placeholder = st.empty()
                status_placeholder.info("Processing video... Please wait.")
                
                # Process the video first
                processed_path, log_path = processor(temp_input_path)
                temp_files.extend([processed_path, log_path])
                
                # Convert processed video
                temp_processed_h264 = tempfile.mktemp(suffix='_processed_h264.mp4')
                temp_files.append(temp_processed_h264)
                
                # Convert both videos to h264
                original_success = convert_video_to_h264(temp_input_path, temp_original_h264)
                processed_success = convert_video_to_h264(processed_path, temp_processed_h264)
                
                if original_success and processed_success:
                    # Clear the processing status
                    status_placeholder.empty()
                    
                    # Create two columns for side-by-side display
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Original Video")
                        with open(temp_original_h264, 'rb') as video_file:
                            video_bytes = video_file.read()
                        st.video(video_bytes, muted=True, autoplay=True)
                    
                    with col2:
                        st.markdown("### Processed Results")
                        with open(temp_processed_h264, 'rb') as video_file:
                            video_bytes = video_file.read()
                        st.video(video_bytes, muted=True, autoplay=True)
                    
                    # Display log in expandable section below both videos
                    if log_path and os.path.exists(log_path):
                        with st.expander("Show Analysis Details"):
                            with open(log_path, 'r') as log:
                                st.text(log.read())
                else:
                    st.error("Error converting video formats")
                
            except Exception as e:
                st.error(f"Error processing video: {str(e)}")
                raise e  # For debugging
            
            finally:
                # Clean up all temporary files
                for file_path in temp_files:
                    try:
                        if file_path and os.path.exists(file_path):
                            os.unlink(file_path)
                    except PermissionError:
                        try:
                            import ctypes
                            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                            kernel32.MoveFileExW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
                            kernel32.MoveFileExW(file_path, None, 4)
                        except:
                            pass
        else:
            st.error("Exercise processor not found!")

def add_video_css():
    st.markdown("""
        <style>
        .stVideo {
            width: 100%;
            margin: 0 auto;
        }
        .video-container video {
            width: 100%;
            max-height: 400px;
            object-fit: contain;
        }
        </style>
    """, unsafe_allow_html=True)

def get_demo_video_path(exercise_name):
    """
    Get the absolute path to the demo video file, checking multiple possible locations.
    """
    # List of possible video file extensions
    extensions = ['.mp4', '.mov', '.avi']
    
    # List of possible directory locations
    possible_dirs = [
        # Current directory
        Path.cwd() / 'demo_videos',
        # One level up
        Path.cwd().parent / 'demo_videos',
        # Relative to the script location
        Path(__file__).parent / 'demo_videos',
    ]
    
    for directory in possible_dirs:
        for ext in extensions:
            video_path = directory / f"{exercise_name}_demo{ext}"
            if video_path.exists():
                return str(video_path)
    
    return None



import requests
import tempfile
import os
import re

def get_drive_file_id(url):
    """Extract file ID from Google Drive URL"""
    file_id = None
    patterns = [
        r'https://drive\.google\.com/file/d/(.*?)/',  # Regular share URL
        r'https://drive\.google\.com/open\?id=(.*?)(?:&|$)',  # Open URL
        r'https://drive\.google\.com/uc\?.*?id=(.*?)(?:&|$)',  # Direct download URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            break
    
    return file_id

def download_from_drive(url):
    """
    Download a file from Google Drive handling large files and redirects
    """
    file_id = get_drive_file_id(url)
    if not file_id:
        raise ValueError("Could not extract Google Drive file ID from URL")

    # Create a session to handle cookies
    session = requests.Session()
    
    try:
        # First, try to get the direct download URL
        download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        response = session.get(download_url, stream=True)
        
        # Check if there's a download warning (large file)
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                download_url = f"{download_url}&confirm={value}"
                response = session.get(download_url, stream=True)
                break
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_path = temp_file.name
        
        # Download the file in chunks
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)
        
        return temp_path
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e
    


import streamlit as st
import tempfile
import os
import requests
import subprocess
from pathlib import Path


from concurrent.futures import ThreadPoolExecutor, as_completed

# Define video URLs at module level
VIDEO_URLS = {
    'pushup': 'https://drive.google.com/file/d/1zN0eRLrj_urOaMxgFujO5UYrzxpsZqnT/view?usp=sharing',
    'deadlift': 'https://drive.google.com/file/d/1o9xksuVOEAmiTjAaQ-K69PdJNOE8ZN1R/view?usp=sharing',
    'bicep': 'https://drive.google.com/file/d/1HXuRYvn0bIsuXw3a-_RPEGWe9XZn97mf/view?usp=sharing'
}

def preload_videos():
    """
    Preload all videos into cache at app startup
    """
    if 'videos_preloaded' not in st.session_state:
        st.session_state.videos_preloaded = False
        
    if not st.session_state.videos_preloaded:
        cache_dir = Path(tempfile.gettempdir()) / 'streamlit_video_cache'
        cache_dir.mkdir(exist_ok=True)
        
        if 'video_cache' not in st.session_state:
            st.session_state.video_cache = {}
        
        # Create a progress container
        progress_container = st.empty()
        with progress_container.container():
            st.write("Initializing exercise videos...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_videos = len(VIDEO_URLS)
            for idx, (exercise_name, url) in enumerate(VIDEO_URLS.items()):
                try:
                    cached_file = cache_dir / f"{exercise_name}_demo_h264.mp4"
                    
                    if not cached_file.exists():
                        status_text.text(f"Downloading {exercise_name} video...")
                        downloaded_path = download_from_drive(url)
                        
                        status_text.text(f"Converting {exercise_name} video...")
                        command = [
                            "ffmpeg",
                            "-i", downloaded_path,
                            "-vcodec", "libx264",
                            "-acodec", "aac",
                            "-y",
                            str(cached_file)
                        ]
                        subprocess.run(command, check=True, capture_output=True)
                        
                        # Clean up downloaded file
                        os.unlink(downloaded_path)
                    
                    st.session_state.video_cache[exercise_name] = str(cached_file)
                    
                except Exception as e:
                    st.error(f"Error processing {exercise_name} video: {str(e)}")
                
                # Update progress
                progress_bar.progress((idx + 1) / total_videos)
                
            # Clean up progress indicators
            progress_container.empty()
            
        st.session_state.videos_preloaded = True

def get_cached_video(exercise_name):
    """
    Get video from cache
    """
    if exercise_name in st.session_state.video_cache:
        cached_path = st.session_state.video_cache[exercise_name]
        if os.path.exists(cached_path):
            return cached_path
    return None

def display_cached_video(exercise_name):
    """
    Display video from cache
    """
    video_path = get_cached_video(exercise_name)
    
    if video_path and os.path.exists(video_path):
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes, muted=True, autoplay=True)
    else:
        st.error(f"Failed to load {exercise_name} video")

def clear_video_cache():
    """
    Clear the video cache
    """
    if 'video_cache' in st.session_state:
        for cached_path in st.session_state.video_cache.values():
            if os.path.exists(cached_path):
                os.unlink(cached_path)
        st.session_state.video_cache = {}
    st.session_state.videos_preloaded = False

# Keep the existing download_from_drive function
def download_from_drive(url):
    """
    Download a file from Google Drive and return the path to the downloaded file
    """
    file_id = url.split('/')[5]  # Extract file ID from the URL
    download_url = f"https://drive.google.com/uc?id={file_id}"
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_path = temp_file.name
    
    # Download the file
    response = requests.get(download_url, stream=True)
    with open(temp_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    
    return temp_path

def convert_to_h264(input_path):
    """Convert video to H264 format"""
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='_h264.mp4')
    temp_output_path = temp_output.name
    temp_output.close()
    
    try:
        command = [
            "ffmpeg",
            "-i", input_path,
            "-vcodec", "libx264",
            "-acodec", "aac",
            "-y",
            temp_output_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            return temp_output_path
        else:
            st.error(f"Conversion error: {result.stderr}")
            os.unlink(temp_output_path)
            return None
            
    except Exception as e:
        st.error(f"Error during conversion: {str(e)}")
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)
        return None



def exercise_page(exercise_name):
    st.markdown(f'<div class="exercise-title">{exercise_name.title()} Form Tracker</div>', unsafe_allow_html=True)
    
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        instructions = {
            'pushup': """
            <div class="exercise-instructions">
                <h2 class="instructions-title">Push-up Instructions:</h2>
                <div class="camera-note">
                    NOTE: Position yourself so your left side faces the camera. 
                    Ensure your full body is visible and only one person is in frame.
                </div>
                <ol>
                    <li>Start in a plank position with hands shoulder-width apart</li>
                    <li>Keep your core tight and back straight</li>
                    <li>Lower your body until chest nearly touches the ground</li>
                    <li>Push back up to starting position</li>
                    <li>Maintain proper form throughout the movement</li>
                </ol>
            </div>
            """,
            'deadlift': """
            <div class="exercise-instructions">
                <h2 class="instructions-title">Deadlift Instructions:</h2>
                <div class="camera-note">
                    NOTE: Position yourself so your left side faces the camera. 
                    Ensure your full body is visible and only one person is in frame.
                </div>
                <ol>
                    <li>Stand with feet hip-width apart</li>
                    <li>Bend at hips and knees to grasp the bar</li>
                    <li>Keep back straight and chest up</li>
                    <li>Push through heels to lift the bar</li>
                    <li>Return to starting position with controlled movement</li>
                </ol>
            </div>
            """,
            'bicep': """
            <div class="exercise-instructions">
                <h2 class="instructions-title">Bicep Curl Instructions:</h2>
                <div class="camera-note">
                    NOTE: Position yourself so your left arm is visible to  the camera. 
                    Ensure your full body is visible and only one person is in frame.
                </div>
                <ol>
                    <li>Stand with feet shoulder-width apart</li>
                    <li>Hold dumbbells at your sides</li>
                    <li>Keep elbows close to your body</li>
                    <li>Curl weights up towards shoulders</li>
                    <li>Lower weights back down with control</li>
                </ol>
            </div>
            """
        }
        st.markdown(instructions[exercise_name], unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Demo Video</p>', unsafe_allow_html=True)
        display_cached_video(exercise_name)
        st.markdown('</div>', unsafe_allow_html=True)

        # Create tabs for upload and live tracking
        tab1, tab2 = st.tabs(["📤 Upload Video", "📹 Live Tracking"])
        
    with tab1:
        st.markdown('<div class="upload-container">', unsafe_allow_html=True)
        add_video_css()  # Add the CSS for video styling
        
        uploaded_file = st.file_uploader(
            "Upload a video for form analysis",
            type=['mp4', 'mov', 'avi'],
            key=f"upload_{exercise_name}"
        )
        
        if uploaded_file:
            handle_video_upload(exercise_name, uploaded_file)
            
        st.markdown('</div>', unsafe_allow_html=True)


        with tab2:
            st.markdown('<div class="live-tracking-container">', unsafe_allow_html=True)
            
            # Add camera permission warning
            st.warning("⚠️ This feature requires camera access. Please ensure your camera is connected and available.")
            
            # Add live tracking button with error handling
            if st.button("Start Live Tracking", key=f"live_{exercise_name}"):
                try:
                    # Check camera availability before starting
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        st.error("Could not access webcam. Please check your camera connection and permissions.")
                        cap.release()
                    else:
                        cap.release()
                        # Show tracking instructions
                        st.info("Press 'q' in the video window to stop tracking")
                        # Start live tracking
                        handle_live_tracking(exercise_name)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    if 'cap' in locals():
                        cap.release()
                    cv2.destroyAllWindows()
            
            # Add helpful tips for live tracking
            with st.expander("Tips for best tracking results"):
                st.markdown("""
                - Ensure good lighting in your workout area
                - Position yourself so your left side faces the camera
                - Keep your full body visible in the frame
                - Wear contrasting clothes to your background
                - Clear the area of other people or moving objects
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Add back button at the bottom of the page
    if st.button("⬅️ Back to Exercise Selection", key=f"back_{exercise_name}"):
        st.session_state.current_page = 'exercise_selection'
        st.rerun()  # Updated from st.experimental_rerun()

def main():
    # Initialize session state variables
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'tracking_active' not in st.session_state:
        st.session_state.tracking_active = False
    
    set_background()
    preload_videos()
    
    if st.session_state.current_page == 'home':
        home_page()
    elif st.session_state.current_page == 'exercise_selection':
        exercise_selection_page()
    elif st.session_state.current_page in ['pushup_page', 'deadlift_page', 'bicep_page']:
        exercise_name = st.session_state.current_page.split('_')[0]
        exercise_page(exercise_name)
    
    if st.session_state.current_page != 'home':
        if st.button("Back to Home", key=f"home_btn_{st.session_state.current_page}"):
            st.session_state.current_page = 'home'
            # Reset tracking state when returning home
            st.session_state.tracking_active = False

if __name__ == "__main__":
    main()
    