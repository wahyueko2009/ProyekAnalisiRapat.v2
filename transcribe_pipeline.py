#!/usr/bin/env python3
import os
import sys
import logging
import torch
import whisperx
import noisereduce as nr
import numpy as np
import ffmpeg
from pyannote.audio import Pipeline
from pyctcdecode import build_ctcdecoder
from deepmultilingualpunctuation import PunctuationModel
import kenlm
import tempfile
import subprocess
from pathlib import Path
import librosa
import soundfile as sf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TranscriptionPipeline:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.whisper_model = None
        self.diarization_pipeline = None
        self.punctuation_model = None
        self.lm_model = None
        self.ctc_decoder = None
        
    def initialize_models(self):
        """Initialize all required models"""
        try:
            # Initialize WhisperX
            self.whisper_model = whisperx.load_model("large-v2", self.device)
            logger.info("WhisperX model loaded successfully")
            
            # Initialize diarization pipeline
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=os.getenv("HUGGINGFACE_TOKEN")
            )
            logger.info("Diarization pipeline loaded successfully")
            
            # Initialize punctuation model
            self.punctuation_model = PunctuationModel()
            logger.info("Punctuation model loaded successfully")
            
            # Initialize KenLM model
            self.lm_model = kenlm.Model("models/id.bin")
            logger.info("KenLM model loaded successfully")
            
            # Initialize CTC decoder
            self.ctc_decoder = build_ctcdecoder(
                labels=[" "] + list("abcdefghijklmnopqrstuvwxyz"),
                kenlm_model_path="models/id.bin"
            )
            logger.info("CTC decoder initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise

    def preprocess_audio(self, audio_path):
        """
        Preprocess audio with noise reduction, high-pass filtering, and volume normalization
        """
        try:
            logger.info("Starting audio preprocessing...")
            
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=None)
            logger.info(f"Audio loaded: {len(audio)/sr:.2f} seconds, {sr}Hz")
            
            # Noise reduction
            logger.info("Applying noise reduction...")
            reduced_noise = nr.reduce_noise(
                y=audio,
                sr=sr,
                prop_decrease=0.75,
                n_fft=2048,
                win_length=2048,
                hop_length=512,
                time_constant_s=2.0,
                freq_mask_smooth_hz=500,
                time_mask_smooth_ms=50
            )
            
            # High-pass filtering
            logger.info("Applying high-pass filter...")
            filtered_audio = librosa.effects.preemphasis(reduced_noise, coef=0.97)
            
            # Volume normalization
            logger.info("Normalizing volume...")
            normalized_audio = librosa.util.normalize(filtered_audio)
            
            # Save preprocessed audio to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(temp_file.name, normalized_audio, sr)
            logger.info(f"Preprocessed audio saved to: {temp_file.name}")
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error in audio preprocessing: {str(e)}")
            raise

    def transcribe_audio(self, audio_path):
        """
        Transcribe audio with speaker diarization and language model rescoring
        """
        try:
            # Preprocess audio
            preprocessed_path = self.preprocess_audio(audio_path)
            
            # Transcribe with WhisperX
            logger.info("Starting transcription...")
            result = self.whisper_model.transcribe(
                preprocessed_path,
                batch_size=16,
                language="id",
                compute_type="float16" if self.device == "cuda" else "float32"
            )
            
            # Apply speaker diarization
            logger.info("Applying speaker diarization...")
            diarize_segments = self.diarization_pipeline(
                preprocessed_path,
                min_speakers=1,
                max_speakers=10
            )
            
            # Combine transcription with speaker labels
            logger.info("Combining transcription with speaker labels...")
            result = whisperx.assign_word_speakers(diarize_segments, result)
            
            # Apply language model rescoring
            logger.info("Applying language model rescoring...")
            for segment in result["segments"]:
                if "text" in segment:
                    # Rescore with KenLM
                    segment["text"] = self.ctc_decoder.decode(segment["text"])
                    
                    # Restore punctuation
                    segment["text"] = self.punctuation_model.restore_punctuation(segment["text"])
            
            # Clean up temporary file
            os.unlink(preprocessed_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in transcription: {str(e)}")
            raise

    def save_transcript(self, result, output_path):
        """
        Save transcript with timestamps and speaker labels
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for segment in result["segments"]:
                    start_time = self.format_timestamp(segment["start"])
                    end_time = self.format_timestamp(segment["end"])
                    speaker = segment.get("speaker", "UNKNOWN")
                    text = segment["text"]
                    
                    f.write(f"[{start_time} --> {end_time}] {speaker}: {text}\n")
                    
            logger.info(f"Transcript saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving transcript: {str(e)}")
            raise

    @staticmethod
    def format_timestamp(seconds):
        """Format seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def main():
    # Initialize pipeline
    pipeline = TranscriptionPipeline()
    pipeline.initialize_models()
    
    # Process audio file
    if len(sys.argv) != 2:
        print("Usage: python transcribe_pipeline.py <audio_file>")
        sys.exit(1)
        
    audio_path = sys.argv[1]
    result = pipeline.transcribe_audio(audio_path)
    
    # Save transcript
    output_path = "transcript.txt"
    pipeline.save_transcript(result, output_path)

if __name__ == "__main__":
    main() 