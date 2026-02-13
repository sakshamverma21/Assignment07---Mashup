# YouTube Mashup Generator

**Live Application:** [https://web-production-0be54f.up.railway.app/](https://web-production-0be54f.up.railway.app/)

## Description

A Python-based web application that generates custom music mashups by downloading YouTube videos, extracting audio segments, and merging them into a single output file. The application provides both a web interface and command-line interface, with automatic email delivery of generated mashups.

## Methodology

### 1. Video Search & Download
- Utilizes `pytubefix` library to search YouTube for videos based on user-specified artist name
- Downloads the top N videos (where N > 10) matching the search query
- Extracts audio-only streams to minimize bandwidth and processing time

### 2. Audio Processing
- Leverages `pydub` library with `ffmpeg` backend for audio manipulation
- Converts downloaded videos to MP4 format with AAC codec (192kbps bitrate)
- Extracts the first Y seconds (where Y > 20) from each audio file

### 3. Mashup Creation
- Concatenates extracted audio segments sequentially
- Exports final mashup as a single MP4 file with consistent audio quality
- Implements automatic cleanup of temporary files upon successful completion

### 4. Delivery
- Packages the mashup file into a ZIP archive
- Sends via SMTP email to the user-specified address
- Uses Gmail App Password authentication for secure delivery

## Features

- **Web Interface**: User-friendly Flask-based frontend with form validation
- **Command-Line Interface**: Direct execution via terminal for automated workflows
- **Input Validation**: Ensures N > 10 videos and Y > 20 seconds duration
- **Error Handling**: Comprehensive exception management with detailed logging
- **Email Delivery**: Automatic ZIP file attachment delivery via Gmail

## Technology Stack

- **Backend**: Python 3.11, Flask
- **Audio Processing**: pydub, ffmpeg, ffprobe
- **YouTube Integration**: pytubefix
- **Deployment**: Railway.app with Gunicorn WSGI server

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure email credentials
echo "SENDER_EMAIL=your_email@gmail.com" > .env
echo "SENDER_PASSWORD=your_app_password" >> .env
```

## Usage

**Web Application:**
```bash
python app.py
# Access at http://localhost:5000
```

**Command Line:**
```bash
python 102303892.py "<Artist Name>" <N_Videos> <Duration_Sec> <Output_File>
# Example: python 102303892.py "Arijit Singh" 15 25 mashup.mp4
```

## Project Structure

```
├── app.py              # Flask web application
├── 102303892.py        # Command-line interface
├── templates/
│   └── index.html      # Frontend interface
├── requirements.txt    # Python dependencies
├── Procfile           # Deployment configuration
└── runtime.txt        # Python version specification
```


