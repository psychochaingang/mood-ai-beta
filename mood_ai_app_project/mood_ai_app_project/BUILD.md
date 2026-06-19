# Mood AI - Android Build Instructions

## Prerequisites
- Linux machine (Ubuntu 22.04+ recommended) 
- OR WSL2 with Ubuntu
- OR Docker (easiest)

## Quick Build (Using Docker - Recommended)

```bash
# 1. Go to the project folder
cd mood_ai_app_project

# 2. Build with Docker (takes 20-40 min first time)
docker run --rm -v $(pwd):/app kivy/buildozer:latest buildozer android debug

# 3. Find your APK in ./bin/
ls bin/*.apk
```

## Manual Build (Ubuntu/Debian)

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 2. Install buildozer
pip3 install --user buildozer cython

# 3. Build
cd mood_ai_app_project
buildozer android debug

# 4. APK location
ls bin/*.apk
```

## Important Notes

### Permissions Required
- CAMERA - for face tracking
- INTERNET - for ads (AdMob)
- RECORD_AUDIO - for mic (future use)

### App Flow (built into the app)
1. Camera permission request
2. Age gate (type age → auto selects Kid/Adult mode)
3. Calibration (7 expressions, 10 samples each)
4. Main app with 5 free trials
5. $2 unlock via in-app purchase (Google Play Billing)

### For Google Play Release
1. Generate a signed APK/AAB:
   ```bash
   buildozer android release
   ```
2. Create a keystore:
   ```bash
   keytool -genkey -v -keystore moodai.keystore -alias moodai -keyalg RSA -keysize 2048 -validity 10000
   ```
3. Update `buildozer.spec` with keystore info
4. Upload the AAB to Google Play Console

### Files in this package
- `main.py` - Main app code
- `buildozer.spec` - Build configuration
- `face_landmarker.task` - AI model (downloads fresh if missing)

## Troubleshooting
- "No module named X" → Add to `requirements` in buildozer.spec
- Camera fails → Check android.permissions includes CAMERA
- MediaPipe crashes → NDK version must be 27b or newer
