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

## Deploy to Render.com (Free & Easy!)

**Simple 5-Step Deployment:**

1. **Sign up** at [Render.com](https://render.com) (free, no credit card required)

2. **Click "New +"** → Select **"Web Service"**

3. **Connect your GitHub repo** (https://github.com/sakshamverma21/Assignment07---Mashup)

4. **Configure:**
   - **Name:** `mashup-app` (or any name)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --timeout 600`
   - **Instance Type:** Free

5. **Add Environment Variables:**
   - `SENDER_EMAIL` = your Gmail address
   - `SENDER_PASSWORD` = your Gmail App Password

Click **"Create Web Service"** - Done! Your app will be live in ~5 minutes. 🚀

**Note:** Render automatically installs ffmpeg on all instances.

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
