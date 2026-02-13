# YouTube Mashup Generator

A web application that creates music mashups by downloading YouTube videos, extracting audio, and merging them into a single file.

## Features

- Download multiple YouTube videos of any singer
- Extract and cut audio to specified duration
- Merge audio clips into a single mashup file
- Send mashup via email as a ZIP file
- Web interface and command-line support

## Requirements

### System Requirements
- Python 3.8+
- ffmpeg (for audio processing)

### Python Dependencies
See `requirements.txt`:
- pytubefix
- pydub
- flask
- python-dotenv

## Installation

### 1. Install ffmpeg

**Windows:**
```powershell
winget install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo dnf install ffmpeg      # Fedora
```

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Email (For Web App)

Create a `.env` file in the project root:

```env
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
```

**To get Gmail App Password:**
1. Enable 2-Factor Authentication on your Google account
2. Visit: https://myaccount.google.com/apppasswords
3. Generate a new App Password
4. Use that password in the `.env` file

## Usage

### Command Line (Program 1)

```powershell
python 102303892.py "Singer Name" NumberOfVideos Duration OutputFile

# Example:
python 102303892.py "Arijit Singh" 15 25 output.mp4
```

**Parameters:**
- Singer Name: Name of the artist (in quotes)
- NumberOfVideos: Number of videos to download (must be > 10)
- Duration: Duration in seconds to cut from each video (must be > 20)
- OutputFile: Output filename (.mp3 or .mp4)

### Web Application (Program 2)

```powershell
python app.py
```

Then open your browser to: http://localhost:5000

Fill in:
- Singer name
- Number of videos (>10)
- Duration in seconds (>20)
- Your email address

You'll receive the mashup file via email.

## Deployment Options

### Option 1: Render (Recommended - Free Tier Available)

1. **Create a `render.yaml` file:**
```yaml
services:
  - type: web
    name: mashup-generator
    env: python
    buildCommand: "pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg"
    startCommand: "gunicorn app:app"
    envVars:
      - key: SENDER_EMAIL
        sync: false
      - key: SENDER_PASSWORD
        sync: false
```

2. **Add `gunicorn` to requirements.txt**

3. **Push to GitHub**

4. **Deploy on Render.com:**
   - Connect your GitHub repo
   - Add environment variables
   - Deploy

### Option 2: PythonAnywhere

1. Upload your files
2. Install dependencies in virtual environment
3. Configure WSGI file
4. Set environment variables
5. Reload web app

**Note:** ffmpeg may not be available on free tier

### Option 3: Railway.app

1. Push to GitHub
2. Connect to Railway
3. Add environment variables
4. Deploy automatically

### Option 4: Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Add buildpack for ffmpeg:
```bash
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

4. Deploy via Git

## Project Structure

```
assignment 7/
├── app.py                  # Flask web application
├── 102303892.py           # Command-line program
├── requirements.txt        # Python dependencies
├── .env                   # Email configuration (not in git)
├── .gitignore            # Git ignore file
├── templates/
│   └── index.html        # Web interface
├── temp_mashups/         # Temporary files (auto-cleanup)
└── README.md            # This file
```

## Important Notes

### Security
- Never commit `.env` file to GitHub
- Use environment variables for production
- Generate new App Passwords for each deployment

### File Formats
- Output format: MP4 (with AAC audio codec)
- Works with any media player

### Cleanup
- Successful mashups: temp files auto-deleted
- Failed mashups: temp files kept for debugging

### Email Configuration
- The web app requires valid Gmail credentials
- Must use App Password, not regular password
- Email configuration is loaded from `.env` file

## Troubleshooting

### "No module named 'pytubefix'"
```powershell
pip install pytubefix
```

### "ffmpeg not found"
Install ffmpeg as per installation instructions above

### "Email not configured"
Create `.env` file with your Gmail credentials

### MP4 file won't play
- Ensure ffmpeg is properly installed
- Check that output file size > 0 bytes
- Try VLC media player

## Assignment Requirements

✅ Program 1: Command-line mashup generator  
✅ Program 2: Web application  
✅ Email delivery of mashup files  
✅ Input validation  
✅ Error handling  

## License

This project is for educational purposes (Assignment submission).
