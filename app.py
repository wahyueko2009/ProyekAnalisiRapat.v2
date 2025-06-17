from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import logging
import warnings
from file_handlers import (
    allowed_file, get_file_size_mb, process_audio_file,
    save_transcript, save_mom, UPLOAD_FOLDER, MAX_CONTENT_LENGTH,
    init_pipeline
)
from prompt_handlers import generate_mom_from_transcript

# Filter warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['MAX_CONTENT_PATH'] = None  # No path length limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize transcription pipeline
try:
    init_pipeline()
    logger.info("Transcription pipeline initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize transcription pipeline: {str(e)}")
    raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info("Received file upload request")
        
        # Validate file presence
        if 'audioFile' not in request.files:
            logger.error("No file in request")
            return jsonify({
                'status': 'error',
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['audioFile']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({
                'status': 'error',
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({
                'status': 'error',
                'error': 'Invalid file type. Use MP3, WAV, M4A, or MP4'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        
        # Validate file size
        file_size_mb = get_file_size_mb(filepath)
        logger.info(f"File size: {file_size_mb:.2f}MB")
        
        if file_size_mb > 250:
            logger.error(f"File too large: {file_size_mb:.2f}MB")
            os.remove(filepath)
            return jsonify({
                'status': 'error',
                'error': f'File size ({file_size_mb:.2f}MB) exceeds maximum limit (250MB)'
            }), 400
        
        try:
            # Process audio file
            result = process_audio_file(filepath)
            transcript = result['transcript']
            
            # Save transcript
            txt_filename = save_transcript(transcript, filename, app.config['UPLOAD_FOLDER'])
            
            # Generate MoM
            mom = None
            mom_filename = None
            
            try:
                logger.info("=== STARTING MoM GENERATION ===")
                logger.info(f"Transcript length for MoM: {len(transcript)} characters")
                
                if not transcript or len(transcript.strip()) < 10:
                    logger.warning("Transcript too short for MoM generation")
                    mom = "Transcript too short to generate meaningful minutes."
                else:
                    mom = generate_mom_from_transcript(transcript)
                
                if mom and len(mom.strip()) > 0:
                    logger.info("✅ MoM generated successfully!")
                    logger.info(f"MoM length: {len(mom)} characters")
                    
                    # Save MoM
                    mom_filename = save_mom(mom, txt_filename, app.config['UPLOAD_FOLDER'])
                    logger.info(f"✅ MoM file saved: {mom_filename}")
                    
                    # Verify file
                    mom_filepath = os.path.join(app.config['UPLOAD_FOLDER'], mom_filename)
                    if os.path.exists(mom_filepath):
                        file_size = os.path.getsize(mom_filepath)
                        logger.info(f"✅ MoM file verified (size: {file_size} bytes)")
                    else:
                        logger.error("❌ MoM file not found after saving!")
                else:
                    logger.warning("⚠️ Empty MoM result")
                    mom = "Failed to generate minutes. Please try again or check audio quality."
                    
            except Exception as e:
                logger.error(f"❌ Error generating MoM: {str(e)}")
                logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                mom = f"Error generating minutes: {str(e)}"
                mom_filename = None
            
            # Prepare response
            if mom_filename:
                success_message = f'File processed successfully (Size: {file_size_mb:.2f}MB, Duration: {result["duration"]} minutes). Minutes saved as {mom_filename}'
            else:
                success_message = f'File processed successfully (Size: {file_size_mb:.2f}MB, Duration: {result["duration"]} minutes). Minutes could not be generated.'
            
            return jsonify({
                'status': 'success',
                'message': success_message,
                'transcript': transcript,
                'txt_file': txt_filename,
                'file_size': f'{file_size_mb:.2f}MB',
                'duration': f'{result["duration"]} minutes',
                'mom': mom,
                'mom_file': mom_filename,
                'mom_status': 'success' if mom_filename else 'failed'
            })
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({
                'status': 'error',
                'error': f'Error processing file: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/test_mom/<txt_file>', methods=['GET'])
def test_mom(txt_file):
    """Endpoint to test MoM generation from existing transcript"""
    try:
        txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_file)
        if not os.path.exists(txt_filepath):
            return jsonify({'status': 'error', 'error': 'Transcript file not found'}), 404

        logger.info(f"Reading file: {txt_filepath}")
        with open(txt_filepath, 'r', encoding='utf-8') as f:
            transcript_text = f.read()

        logger.info(f"Transcript length: {len(transcript_text)} characters")
        
        # Generate MoM
        logger.info("Starting MoM generation from test endpoint...")
        mom = generate_mom_from_transcript(transcript_text)
        
        if mom:
            # Save MoM
            mom_filename = save_mom(mom, txt_file, app.config['UPLOAD_FOLDER'])
            logger.info(f"MoM file saved: {mom_filename}")
            
            return jsonify({
                'status': 'success', 
                'mom': mom, 
                'mom_file': mom_filename,
                'message': f'Minutes generated from {txt_file}'
            })
        else:
            return jsonify({'status': 'error', 'error': 'Could not generate minutes'}), 500
            
    except Exception as e:
        logger.error(f"Error testing MoM: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/generate_mom', methods=['POST'])
def generate_mom():
    """Endpoint to generate MoM from transcript"""
    data = request.json
    txt_filename = data.get('txt_file')
    if not txt_filename:
        return jsonify({'status': 'error', 'error': 'No transcript file specified'}), 400

    txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
    if not os.path.exists(txt_filepath):
        return jsonify({'status': 'error', 'error': 'Transcript file not found'}), 404

    with open(txt_filepath, 'r', encoding='utf-8') as f:
        transcript_text = f.read()

    try:
        mom = generate_mom_from_transcript(transcript_text)
        mom_filename = save_mom(mom, txt_filename, app.config['UPLOAD_FOLDER'])
        return jsonify({'status': 'success', 'mom': mom, 'mom_file': mom_filename})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_uploads():
    """Clear all files in uploads folder"""
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting file {filename}: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'error': f'Failed to delete some files: {str(e)}'
                }), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Uploads folder cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing folder: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f'An error occurred: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 