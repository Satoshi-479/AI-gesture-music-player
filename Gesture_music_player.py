
import cv2
import time
import os
import subprocess
import shutil
from collections import deque
import numpy as np
import mediapipe as mp

try:
    import pygame
except ImportError:
    import pygame_ce as pygame

# ============================================================================
# CONFIGURATION (List your original files here, the script handles the rest!)
# ============================================================================

SONGS = {
    1: "songs/1.wav",
    2: "songs/2.mp3",
    3: "songs/3.wav",
    4: "songs/4.wav",
    5: "songs/5.mp3",
    7: "songs/7.mp3",
    8: "songs/8.mp3",
    9: "songs/9.mp3",
    10: "songs/10.mp3",
}

SONG_REPLAY_DELAY = 3
STABILITY_WINDOW = 10
STABILITY_THRESHOLD = 8
VOLUME_SMOOTH_FACTOR = 0.1

COLORS = {
    'primary':   (0, 255, 200),
    'secondary': (255, 100, 200),
    'success':   (100, 255, 150),
    'warning':   (255, 200, 0),
    'text_gray': (150, 150, 180),
    'red':       (0, 0, 255),
    'white':     (255, 255, 255),
}

# ============================================================================
# AUTOMATED FFMPEG AUDIO SANITIZATION
# ============================================================================

def auto_sanitize_songs(songs_dict):
    """Detects ffmpeg and automatically fixes problematic MP3s on the fly."""
    print("🔄 Checking audio files for Pygame compatibility...")
    ffmpeg_available = shutil.which("ffmpeg") is not None
    
    cleaned_songs = {}
    
    for finger_count, file_path in songs_dict.items():
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: File missing for gesture {finger_count}: {file_path}")
            cleaned_songs[finger_count] = file_path
            continue
            
        # If it's an MP3, try to clean it and turn it into a WAV
        if file_path.lower().endswith('.mp3'):
            wav_path = os.path.splitext(file_path)[0] + ".wav"
            
            # If we already created the fixed WAV file previously, use it!
            if os.path.exists(wav_path):
                cleaned_songs[finger_count] = wav_path
                continue
                
            if ffmpeg_available:
                print(f"🎬 ffmpeg detected! Stripping metadata & converting: {file_path} -> {wav_path}")
                try:
                    # Run the background conversion stripping out images and tags
                    cmd = [
                        "ffmpeg", "-y", "-i", file_path, 
                        "-map", "0:a", "-map_metadata", "-1", 
                        "-c:a", "pcm_s16le", "-ar", "44100", wav_path
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    cleaned_songs[finger_count] = wav_path
                except Exception as e:
                    print(f"❌ ffmpeg failed converting {file_path}: {e}")
                    cleaned_songs[finger_count] = file_path
            else:
                print(f"⚠️ Found MP3 ({file_path}) but 'ffmpeg' isn't in your Windows PATH. Pygame may crash.")
                cleaned_songs[finger_count] = file_path
        else:
            # Already a WAV file, it's perfectly safe
            cleaned_songs[finger_count] = file_path
            
    print("✅ Audio optimization check complete!\n")
    return cleaned_songs

# ============================================================================
# AUDIO MIXER ENGINE
# ============================================================================

def init_audio():
    try:
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        print("✅ Audio mixer initialized")
    except Exception as e:
        print(f"❌ Mixer init failed: {e}")
        return False
    return True


class SongPlayer:
    def __init__(self, songs_dict):
        self.songs = songs_dict
        self.last_played_time = 0
        self.last_played_song = None
        self.volume = 0.7
        self.target_volume = 0.7
        self.current_song_name = ""
        self.broken_songs = set()
        pygame.mixer.music.set_volume(self.volume)

    def play_song(self, finger_count):
        if finger_count in self.broken_songs:
            return False

        current_time = time.time()
        if current_time - self.last_played_time < SONG_REPLAY_DELAY:
            return False

        song_file = self.songs.get(finger_count)
        if not song_file or not os.path.exists(song_file):
            return False

        if finger_count == self.last_played_song and pygame.mixer.music.get_busy():
            return False

        try:
            pygame.mixer.music.load(song_file)
            pygame.mixer.music.play()
            self.last_played_song = finger_count
            self.last_played_time = current_time
            self.current_song_name = os.path.splitext(os.path.basename(song_file))[0]
            print(f"🎵 NOW PLAYING: Song {finger_count} ({self.current_song_name})")
            return True
        except Exception as e:
            self.broken_songs.add(finger_count)
            print(f"\n❌ Song {finger_count} FAILED: {e}\n")
            return False

    def set_volume(self, volume):
        self.target_volume = max(0.0, min(1.0, volume))
        self.volume += (self.target_volume - self.volume) * VOLUME_SMOOTH_FACTOR
        pygame.mixer.music.set_volume(self.volume)

    def stop_song(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    if not init_audio():
        return

    # Automatically clean up the audio tracks using ffmpeg before running the camera
    optimized_songs = auto_sanitize_songs(SONGS)

    # Initialize MediaPipe Hands via direct environment link
    mp_hands = mp.solutions.hands
    hands_model = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    player = SongPlayer(optimized_songs)
    finger_history = deque(maxlen=STABILITY_WINDOW)
    current_finger_count = 0
    muted = False

    print("=" * 70)
    print("🤖 AI GESTURE MUSIC PLAYER - METADATA CLEANED")
    print("=" * 70)
    print("⌨️  Q=Quit | SPACE=Stop | M=Mute\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1) # Mirror image
        h, w, c = frame.shape
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_model.process(rgb_frame)

        hand_detected = False
        total_fingers = 0
        avg_y_norm = 0.5 

        if results.multi_hand_landmarks:
            hand_detected = True
            y_positions = []
            
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                handedness = results.multi_handedness[hand_idx].classification[0].label
                fingers_open = 0
                
                # 1. Check Thumb
                if handedness == "Right":
                    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                        fingers_open += 1
                else: 
                    if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                        fingers_open += 1
                        
                # 2. Check 4 Fingers
                for tip_id in [8, 12, 16, 20]:
                    if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
                        fingers_open += 1
                        
                total_fingers += fingers_open
                y_positions.append(hand_landmarks.landmark[9].y)

            avg_y_norm = sum(y_positions) / len(y_positions)
            volume_level = 1.0 - avg_y_norm
            player.set_volume(volume_level)
            finger_history.append(total_fingers)
        else:
            finger_history.clear()

        if len(finger_history) == STABILITY_WINDOW:
            stable_count = max(set(finger_history), key=finger_history.count)
            most_common_count = finger_history.count(stable_count)
            
            if most_common_count >= STABILITY_THRESHOLD:
                if stable_count != current_finger_count:
                    current_finger_count = stable_count
                    if 1 <= current_finger_count <= 10:
                        player.play_song(current_finger_count)

        # ====================================================================
        # ON-SCREEN UI
        # ====================================================================
        vb_x, vb_y, vb_h = 20, int(h * 0.15), int(h * 0.7)
        cv2.rectangle(frame, (vb_x, vb_y), (vb_x + 15, vb_y + vb_h), COLORS['text_gray'], 2)
        fill_h = int(vb_h * player.volume)
        cv2.rectangle(frame, (vb_x, vb_y + vb_h - fill_h), (vb_x + 15, vb_y + vb_h), COLORS['warning'], -1)

        cv2.putText(frame, "AI GESTURE MUSIC PLAYER", (40, 40), cv2.FONT_HERSHEY_DUPLEX, 1.2, COLORS['primary'], 2)
        
        detect_text = "HAND DETECTED" if hand_detected else "NO HAND"
        detect_color = COLORS['success'] if hand_detected else COLORS['red']
        cv2.putText(frame, detect_text, (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, detect_color, 2)

        y_pos = h // 2
        cv2.circle(frame, (w // 2, y_pos), 60, COLORS['secondary'], -1)
        cv2.circle(frame, (w // 2, y_pos), 60, COLORS['primary'], 3)
        digit_color = COLORS['white'] if current_finger_count > 0 else COLORS['text_gray']
        cv2.putText(frame, str(current_finger_count), (w // 2 - 25, y_pos + 25), cv2.FONT_HERSHEY_DUPLEX, 3, digit_color, 3)

        song_text = player.current_song_name if player.current_song_name else "No song"
        cv2.putText(frame, f"Now: {song_text[:25]}", (40, y_pos + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['secondary'], 2)
        cv2.putText(frame, f"VOLUME: {int(player.volume * 100)}%", (w - 280, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['text_gray'], 1)

        cv2.imshow("Gesture Music Player", frame)

        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            player.stop_song()
        elif key == ord('m'):
            if muted:
                player.set_volume(getattr(player, 'pre_mute_vol', 0.7))
                muted = False
            else:
                player.pre_mute_vol = player.target_volume
                player.set_volume(0)
                muted = True
        elif ord('1') <= key <= ord('9'):
            player.play_song(key - ord('0'))
        elif key == ord('0'):
            player.play_song(10)

    hands_model.close()
    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()
    print("✅ Closed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")