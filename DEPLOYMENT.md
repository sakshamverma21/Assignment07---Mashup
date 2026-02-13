# Quick Deployment Guide

## ✅ Recommended: Render.com (FREE)

### Why Render?
- ✅ Free tier available
- ✅ Easy ffmpeg installation
- ✅ Auto-deployment from GitHub
- ✅ Environment variables support
- ✅ Custom domains

### Steps:

1. **Push to GitHub**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/mashup-app.git
   git push -u origin main
   ```

2. **Create Render Account**
   - Go to: https://render.com
   - Sign up with GitHub

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** mashup-generator
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`

4. **Add Environment Variables**
   - Go to "Environment" tab
   - Add:
     - `SENDER_EMAIL` = your_email@gmail.com
     - `SENDER_PASSWORD` = your_app_password

5. **Install ffmpeg**
   - In "Environment" tab, add:
     - Click "Add Environment Variable"
     - Key: `PYTHON_VERSION`
     - Value: `3.11.9`
   - In "Settings" → "Build & Deploy"
   - Add to Build Command:
     ```
     apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
     ```

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your app will be live at: https://your-app-name.onrender.com

---

## Alternative: Railway.app (Very Easy)

### Steps:

1. **Push to GitHub** (same as above)

2. **Deploy on Railway**
   - Go to: https://railway.app
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Environment Variables**
   - Go to Variables tab
   - Add `SENDER_EMAIL` and `SENDER_PASSWORD`

4. **Install ffmpeg**
   - Go to Settings
   - Add Nixpacks buildpack
   - Create `nixpacks.toml`:
     ```toml
     providers = ["python"]
     
     [phases.setup]
     aptPkgs = ["ffmpeg"]
     ```

5. **Deploy automatically!**

---

## Alternative: Heroku (Classic Option)

### Steps:

1. **Install Heroku CLI**
   ```powershell
   winget install Heroku.HerokuCLI
   ```

2. **Login and Create App**
   ```powershell
   heroku login
   heroku create your-app-name
   ```

3. **Add ffmpeg Buildpack**
   ```powershell
   heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   heroku buildpacks:add --index 2 heroku/python
   ```

4. **Set Environment Variables**
   ```powershell
   heroku config:set SENDER_EMAIL=your_email@gmail.com
   heroku config:set SENDER_PASSWORD=your_app_password
   ```

5. **Deploy**
   ```powershell
   git push heroku main
   ```

6. **Open App**
   ```powershell
   heroku open
   ```

**Note:** Heroku removed free tier, but you can use student credits

---

## For Assignment Submission

### Option 1: Deploy and Submit Link
Deploy on Render/Railway and submit the live URL

### Option 2: Local Hosting + Ngrok
If you just need a temporary link for testing:

```powershell
# Install ngrok
winget install ngrok

# Run your Flask app
python app.py

# In another terminal, expose it
ngrok http 5000
```

This gives you a public URL like: `https://abc123.ngrok.io`

**Warning:** Ngrok links expire after session ends

---

## Testing Your Deployed App

1. Visit your deployed URL
2. Fill in the form:
   - Singer: "Arijit Singh"
   - Videos: 11
   - Duration: 25
   - Your email
3. Wait for email (may take 2-5 minutes)
4. Check spam folder if not received

---

## Troubleshooting Deployment

### "Application Error" on Render
- Check logs in Render dashboard
- Verify ffmpeg is in build command
- Ensure environment variables are set

### Email not sending
- Verify `SENDER_EMAIL` and `SENDER_PASSWORD` are set
- Check Gmail App Password is correct
- Verify 2FA is enabled on Gmail

### Timeout errors
- Increase timeout in Procfile: `--timeout 600`
- Reduce number of videos to test
- Check Render logs for specific errors

### ffmpeg not found
- Add ffmpeg to build command
- For Render: `apt-get install -y ffmpeg`
- For Railway: Use nixpacks.toml
- For Heroku: Use buildpack

---

## Best Deployment for This Project

**🏆 Recommendation: Render.com**
- Easiest setup
- Free tier
- Good for educational projects
- Supports ffmpeg easily
- Auto-deploys from GitHub

Good luck with your deployment! 🚀
