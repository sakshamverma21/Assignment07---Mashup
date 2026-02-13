"""
Mashup Web Application
Allows users to create YouTube mashups via web interface and receive results via email
"""

from flask import Flask, render_template, request, jsonify
from pytubefix import YouTube, Search
from pydub import AudioSegment
import os
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import zipfile
import threading
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure ffmpeg and ffprobe paths for pydub
ffmpeg_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 
                           'Microsoft', 'WinGet', 'Packages',
                           'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe',
                           'ffmpeg-8.0.1-full_build', 'bin', 'ffmpeg.exe')
ffprobe_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 
                            'Microsoft', 'WinGet', 'Packages',
                            'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe',
                            'ffmpeg-8.0.1-full_build', 'bin', 'ffprobe.exe')
if os.path.exists(ffmpeg_path):
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    print(f"Using ffmpeg from: {ffmpeg_path}")
    print(f"Using ffprobe from: {ffprobe_path}")
else:
    print("Warning: ffmpeg not found at expected location, using system PATH")
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'temp_mashups'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Email configuration
# IMPORTANT: Update these with your actual Gmail credentials before running
# For Gmail, you need to:
# 1. Enable 2-Factor Authentication on your Google account
# 2. Generate an App Password: https://myaccount.google.com/apppasswords
# 3. Use the App Password (not your regular Gmail password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "your_email@gmail.com")  # Update this or set environment variable
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "your_app_password")  # Update this or set environment variable


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_mashup(singer_name, num_videos, duration, user_email, task_id):
    """Create mashup in background thread"""
    temp_dir = os.path.join(UPLOAD_FOLDER, f"task_{task_id}")
    
    try:
        # Create task directory
        os.makedirs(temp_dir, exist_ok=True)
        
        print(f"Task {task_id}: Starting mashup creation for {singer_name}")
        
        # Search and download videos
        print(f"Task {task_id}: Searching for videos...")
        search = Search(singer_name)
        results = search.results
        
        if not results:
            raise Exception(f"No search results found for '{singer_name}'. Try a different or more common name.")
        
        print(f"Task {task_id}: Found {len(results)} videos, will download first {num_videos}")
        
        downloaded_files = []
        for i, video in enumerate(results[:num_videos]):
            try:
                print(f"Task {task_id}: Downloading video {i+1}/{num_videos}: {video.title[:50]}")
                audio_stream = video.streams.filter(only_audio=True).first()
                if audio_stream:
                    output_path = audio_stream.download(
                        output_path=temp_dir,
                        filename=f"video_{i}.mp4"
                    )
                    downloaded_files.append(output_path)
                    print(f"Task {task_id}: Successfully downloaded video {i+1}")
                else:
                    print(f"Task {task_id}: No audio stream available for video {i+1}")
            except Exception as e:
                print(f"Task {task_id}: Error downloading video {i+1}: {str(e)}")
                continue
        
        if not downloaded_files:
            raise Exception(f"No videos were successfully downloaded. This can happen if:\n"
                          f"1. The singer name '{singer_name}' returned no results\n"
                          f"2. All videos failed to download (network issues)\n"
                          f"3. YouTube API restrictions\n"
                          f"Try using a more common or different spelling of the singer name.")
        
        print(f"Task {task_id}: Successfully downloaded {len(downloaded_files)} out of {num_videos} videos")
        
        # Convert to audio and cut
        print(f"Task {task_id}: Processing audio files...")
        combined = AudioSegment.empty()
        
        for i, video_file in enumerate(downloaded_files):
            try:
                print(f"Task {task_id}: Processing audio from video {i+1}/{len(downloaded_files)}")
                audio = AudioSegment.from_file(video_file)
                print(f"Task {task_id}: Video {i+1} loaded, duration: {len(audio)/1000:.2f}s")
                cut_audio = audio[:duration * 1000]  # Cut to specified duration
                print(f"Task {task_id}: Video {i+1} cut to {duration}s")
                combined += cut_audio
                print(f"Task {task_id}: Video {i+1} added to combined audio")
            except Exception as e:
                print(f"Task {task_id}: Error processing audio {i+1}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Export merged audio as MP4
        output_file = os.path.join(temp_dir, f"mashup_{task_id}.mp4")
        print(f"Task {task_id}: Exporting combined audio to {output_file}")
        print(f"Task {task_id}: Combined audio duration: {len(combined)/1000:.2f}s")
        
        try:
            combined.export(
                output_file, 
                format='mp4',
                codec='aac',
                bitrate='192k'
            )
            print(f"Task {task_id}: Export completed successfully")
            
            # Check file size
            file_size = os.path.getsize(output_file)
            print(f"Task {task_id}: Output file size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Output file is empty (0 bytes)")
                
        except Exception as e:
            print(f"Task {task_id}: ERROR during export: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        # Create zip file
        zip_path = os.path.join(temp_dir, f"mashup_{task_id}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(output_file, os.path.basename(output_file))
        
        # Send email
        print(f"Task {task_id}: Sending email to {user_email}")
        send_email(user_email, zip_path, singer_name)
        
        print(f"Task {task_id}: Completed successfully")
        
        # Cleanup after successful completion
        try:
            shutil.rmtree(temp_dir)
            print(f"Task {task_id}: Cleaned up temp files")
        except Exception as e:
            print(f"Task {task_id}: Warning - Could not clean up temp files: {str(e)}")
        
    except Exception as e:
        print(f"Task {task_id}: Error - {str(e)}")
        # Send error email
        try:
            send_error_email(user_email, singer_name, str(e))
        except:
            pass
        # Keep temp files on error for debugging
        print(f"Task {task_id}: Keeping temp files in {temp_dir} for debugging due to error")


def send_email(recipient_email, zip_path, singer_name):
    """Send email with zip file attachment"""
    try:
        # Check if email is configured
        if SENDER_EMAIL == "your_email@gmail.com" or SENDER_PASSWORD == "your_app_password":
            print("ERROR: Email not configured! Please update SENDER_EMAIL and SENDER_PASSWORD in app.py")
            raise Exception("Email configuration required. Please check the console for instructions.")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"Your {singer_name} Mashup is Ready!"
        
        # Email body
        body = f"""
Hello!

Your mashup for {singer_name} has been created successfully.

Please find the attached zip file containing your mashup.

Enjoy your music!

Best regards,
Mashup Generator Team
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach zip file
        with open(zip_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(zip_path)}'
        )
        msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent successfully to {recipient_email}")
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise


def send_error_email(recipient_email, singer_name, error_message):
    """Send error notification email"""
    try:
        if SENDER_EMAIL == "your_email@gmail.com" or SENDER_PASSWORD == "your_app_password":
            return
            
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"Error Creating {singer_name} Mashup"
        
        body = f"""
Hello!

Unfortunately, there was an error creating your mashup for {singer_name}.

Error: {error_message}

Please try again with different parameters or contact support.

Best regards,
Mashup Generator Team
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
    except Exception as e:
        print(f"Error sending error notification: {str(e)}")


@app.route('/')
def index():
    """Render home page"""
    return render_template('index.html')


@app.route('/create-mashup', methods=['POST'])
def create_mashup_endpoint():
    """Handle mashup creation request"""
    try:
        # Get form data
        singer_name = request.form.get('singer_name', '').strip()
        num_videos = request.form.get('num_videos', '').strip()
        duration = request.form.get('duration', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validate inputs
        if not singer_name:
            return jsonify({'error': 'Singer name is required'}), 400
        
        if not num_videos or not num_videos.isdigit() or int(num_videos) <= 10:
            return jsonify({'error': 'Number of videos must be greater than 10'}), 400
        
        if not duration or not duration.isdigit() or int(duration) <= 20:
            return jsonify({'error': 'Duration must be greater than 20 seconds'}), 400
        
        if not email or not validate_email(email):
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        # Convert to integers
        num_videos = int(num_videos)
        duration = int(duration)
        
        # Generate task ID
        import time
        task_id = str(int(time.time()))
        
        # Start background thread
        thread = threading.Thread(
            target=create_mashup,
            args=(singer_name, num_videos, duration, email, task_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Your mashup is being created! You will receive an email at {email} once it\'s ready. This may take several minutes.',
            'task_id': task_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    # Print startup instructions
    print("\n" + "="*60)
    print("YouTube Mashup Web Application")
    print("="*60)
    print("\nIMPORTANT: Email Configuration Required!")
    print("-" * 60)
    print("Before using this application, you must configure email:")
    print("1. Open app.py")
    print("2. Update SENDER_EMAIL with your Gmail address")
    print("3. Update SENDER_PASSWORD with your Gmail App Password")
    print("\nTo get Gmail App Password:")
    print("- Enable 2FA on your Google account")
    print("- Visit: https://myaccount.google.com/apppasswords")
    print("- Generate a new App Password")
    print("\nAlternatively, set environment variables:")
    print("  set SENDER_EMAIL=your_email@gmail.com")
    print("  set SENDER_PASSWORD=your_app_password")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
