import os
import logging
import whisper
import librosa
from transcribe_pipeline import TranscriptionPipeline

# Setup logging
logger = logging.getLogger(__name__)

# Constants
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 250 * 1024 * 1024  # 250MB in bytes

# Initialize transcription pipeline
transcription_pipeline = None

def init_pipeline():
    """Initialize the transcription pipeline"""
    global transcription_pipeline
    try:
        transcription_pipeline = TranscriptionPipeline(model_size="medium")
        logger.info("Transcription pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize transcription pipeline: {str(e)}")
        raise

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'mp4'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def process_audio_file(filepath):
    """Process audio file using the new pipeline"""
    try:
        if transcription_pipeline is None:
            init_pipeline()
        
        # Process audio and get transcript with speaker diarization
        result = transcription_pipeline.transcribe(filepath)
        
        # Calculate duration
        duration = librosa.get_duration(path=filepath)
        duration_minutes = round(duration / 60, 1)
        
        # Format transcript for MoM generation
        formatted_transcript = format_transcript_for_mom(result)
        
        return {
            'transcript': formatted_transcript,
            'duration': duration_minutes,
            'raw_result': result  # Keep the full result for potential future use
        }
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise

def format_transcript_for_mom(result):
    """Format transcript for MoM generation"""
    formatted_lines = []
    
    for segment in result["segments"]:
        start_time = format_timestamp(segment["start"])
        speaker = segment.get("speaker", "Unknown")
        text = segment["text"]
        
        formatted_lines.append(f"[{start_time}] {speaker}: {text}")
    
    return "\n".join(formatted_lines)

def format_timestamp(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def save_transcript(transcript, filename, upload_folder):
    """Save transcript to file"""
    txt_filename = os.path.splitext(filename)[0] + '.txt'
    txt_filepath = os.path.join(upload_folder, txt_filename)
    
    with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write(transcript)
    
    return txt_filename

def save_mom(mom_text, txt_filename, upload_folder):
    """Save MoM to file"""
    mom_filename = txt_filename.replace('.txt', '.mom.txt')
    mom_filepath = os.path.join(upload_folder, mom_filename)
    
    with open(mom_filepath, 'w', encoding='utf-8') as f:
        f.write(mom_text)
    
    return mom_filename 