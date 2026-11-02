# 🎵 AI Gesture Music Player

[![Live Demo](https://img.shields.io/badge/Live_Demo-Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white)](https://gesturemusicplayer.netlify.app/)
[![GitHub repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Satoshi-479/AI-gesture-music-player)

An interactive AI-powered music player that tracks your hand gestures in real-time using **MediaPipe** and **OpenCV** to control audio playback and select songs.

> 🚀 **Live Demo:** Try the web player instantly in your browser at **[gesturemusicplayer.netlify.app](https://gesturemusicplayer.netlify.app/)**!

Includes both a **Python Desktop Application** (with Pygame and FFmpeg sanitization) and an **Interactive Web UI** (`index.html`) deployed on Netlify.

---

## ✨ Features

- **Real-Time Hand Tracking**: Uses MediaPipe's `hand_landmarker.task` for fast, low-latency finger counting and gesture detection.
- **Gesture-to-Song Mapping**:
  - Show 1 to 10 fingers to trigger mapped songs.
  - Closed fist (0 fingers) to stop/pause music.
- **Smart Audio Sanitization**: Automatically detects FFmpeg to strip corrupted metadata and convert MP3s to high-performance PCM WAV format on the fly for seamless Pygame playback.
- **Volume & Playback Controls**: Dynamic gesture-based stabilization to prevent accidental song switching.
- **Web Interface Included**: Open `index.html` in any modern browser for a camera-enabled, client-side web version.

---

## 📁 Project Structure

```text
AI-gesture-music-player/
│
├── Gesture_music_player.py    # Main Python desktop application
├── index.html                 # Browser-based interactive gesture player
├── hand_landmarker.task       # MediaPipe Hand Landmarker model
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── songs/                     # Directory for your music tracks (.mp3 / .wav)
    └── .gitkeep
```

---

## 🚀 Getting Started (Python App)

### 1. Prerequisites
- Python 3.9+
- Webcam
- *(Optional)* [FFmpeg](https://ffmpeg.org/) installed and added to PATH for automatic MP3 sanitization.

### 2. Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Satoshi-479/AI-gesture-music-player.git
   cd AI-gesture-music-player
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Add Songs

Place your favorite audio files into the `songs/` folder corresponding to the finger counts:
- `songs/1.mp3` or `1.wav` (1 Finger)
- `songs/2.mp3` or `2.wav` (2 Fingers)
- `songs/3.mp3` or `3.wav` (3 Fingers)
- ... up to 10 fingers (using both hands).

### 4. Run the Application

```bash
python Gesture_music_player.py
```

Press `q` or `ESC` in the camera window to exit.

---

## 🌐 Web Version

### 🚀 Live Demo (Online)
No installation required! Simply open the hosted application:
👉 **[gesturemusicplayer.netlify.app](https://gesturemusicplayer.netlify.app/)**

1. Allow webcam access when prompted.
2. Show your hand gestures to the camera to trigger music.

### 💻 Running Locally
If you prefer running the web version locally:
1. Double-click `index.html` or serve via a local HTTP server:
   ```bash
   python -m http.server 8000
   ```
2. Open `http://localhost:8000` in your browser.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

