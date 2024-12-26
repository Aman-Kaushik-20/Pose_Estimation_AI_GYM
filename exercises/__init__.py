from .uploaded_pushup_track import process_video as pushup_process_video
from .uploaded_deadlift_track import process_video as deadlift_process_video
from .uploaded_bicep_track import process_video as bicep_process_video

__all__ = ['pushup_process_video', 'deadlift_process_video', 'bicep_process_video']