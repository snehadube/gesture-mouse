"""
Gesture Mouse — control your mouse with hand gestures + voice commands.

Left click   : pinch Index finger + Thumb
Right click  : pinch Middle finger + Thumb
Scroll down  : pinch Ring finger + Thumb
Voice        : say "chrome" / "notepad" / "music" / "close"

Press ESC to quit.
"""

import subprocess
import threading
import time

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import pyttsx3
import speech_recognition as sr
import tkinter as tk

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
COOLDOWN_TIME = 0.5           # seconds between repeated clicks/scrolls
CLICK_DISTANCE_THRESHOLD = 40  # pixels, how close fingers must be to "pinch"
SMOOTHENING = 5                # higher = smoother but laggier cursor
LOG_FILE = "log.txt"

pyautogui.FAILSAFE = True  # move mouse to a screen corner to abort if it goes crazy

# cooldown trackers (module-level state, updated inside main loop)
last_left_click = 0.0
last_right_click = 0.0
last_scroll = 0.0


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def log_action(action: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}\n")


# ---------------------------------------------------------------------------
# Voice command thread
# ---------------------------------------------------------------------------
def listen_voice() -> None:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    engine = pyttsx3.init()  # init ONCE, not every loop (was a bug before)

    while True:
        with mic as source:
            print("Speak Command:")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            except sr.WaitTimeoutError:
                print("Voice input timeout, try again.")
                continue

        try:
            command = recognizer.recognize_google(audio, language="en-IN").lower()
            print("You said:", command)

            if "chrome" in command:
                pyautogui.hotkey("win", "r")
                time.sleep(0.5)
                pyautogui.typewrite("chrome\n")
                engine.say("Opening Chrome")
                engine.runAndWait()
                log_action("Opened Chrome via voice")

            elif "notepad" in command:
                subprocess.Popen("notepad.exe")
                engine.say("Opening Notepad")
                engine.runAndWait()
                log_action("Opened Notepad via voice")

            elif "music" in command:
                pyautogui.hotkey("win", "r")
                time.sleep(0.5)
                pyautogui.typewrite("wmplayer\n")
                engine.say("Opening Music Player")
                engine.runAndWait()
                log_action("Opened Music Player via voice")

            elif "close" in command:
                pyautogui.hotkey("alt", "f4")
                engine.say("Closing Window")
                engine.runAndWait()
                log_action("Closed window via voice")

        except sr.UnknownValueError:
            print("Sorry, I did not understand. Please repeat.")
        except Exception as e:  # noqa: BLE001 - keep voice thread alive no matter what
            print("Voice error:", e)


# ---------------------------------------------------------------------------
# One-time instructions popup
# ---------------------------------------------------------------------------
def show_instructions() -> None:
    root = tk.Tk()
    root.title("Gesture Mouse Instructions")
    root.geometry("500x400")
    root.configure(bg="lightblue")

    instructions = """
    GESTURE INSTRUCTIONS:
    - Move cursor: Move index finger
    - Left Click: Pinch (Index + Thumb)
    - Right Click: Pinch (Middle + Thumb)
    - Scroll Down: Pinch (Ring + Thumb)

    VOICE COMMANDS:
    - 'Chrome'  -> Open Chrome
    - 'Notepad' -> Open Notepad
    - 'Music'   -> Open Music Player
    - 'Close'   -> Close active window

    Press ESC to Exit Program
    """

    label = tk.Label(
        root, text=instructions, font=("Arial", 12), justify="left", bg="lightblue"
    )
    label.pack(padx=20, pady=20)

    root.after(4000, root.destroy)  # auto-close after 4 seconds
    root.mainloop()


# ---------------------------------------------------------------------------
# Main gesture-mouse loop
# ---------------------------------------------------------------------------
def main() -> None:
    global last_left_click, last_right_click, last_scroll

    show_instructions()

    voice_thread = threading.Thread(target=listen_voice, daemon=True)
    voice_thread.start()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    screen_width, screen_height = pyautogui.size()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: could not access the webcam. Check camera permissions / index.")
        return

    prev_x, prev_y = 0.0, 0.0

    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Error: failed to read frame from webcam.")
                break

            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result = hands.process(img_rgb)

            # img.shape is (height, width, channels) -> use [1] for width, [0] for height
            h, w, _ = img.shape

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    x = int(hand_landmarks.landmark[8].x * w)
                    y = int(hand_landmarks.landmark[8].y * h)

                    x_thumb = int(hand_landmarks.landmark[4].x * w)
                    y_thumb = int(hand_landmarks.landmark[4].y * h)

                    x_middle = int(hand_landmarks.landmark[12].x * w)
                    y_middle = int(hand_landmarks.landmark[12].y * h)

                    x_ring = int(hand_landmarks.landmark[16].x * w)
                    y_ring = int(hand_landmarks.landmark[16].y * h)

                    mp_draw.draw_landmarks(
                        img, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )

                    # Map index-finger position to screen coordinates
                    screen_x = np.interp(x, [0, w], [0, screen_width])
                    screen_y = np.interp(y, [0, h], [0, screen_height])

                    curr_x = prev_x + (screen_x - prev_x) / SMOOTHENING
                    curr_y = prev_y + (screen_y - prev_y) / SMOOTHENING
                    pyautogui.moveTo(curr_x, curr_y)
                    prev_x, prev_y = curr_x, curr_y

                    current_time = time.time()

                    # Left click: Index + Thumb pinch
                    if (
                        np.hypot(x - x_thumb, y - y_thumb) < CLICK_DISTANCE_THRESHOLD
                        and (current_time - last_left_click) > COOLDOWN_TIME
                    ):
                        pyautogui.click()
                        cv2.circle(img, (x, y), 15, (0, 255, 0), cv2.FILLED)
                        last_left_click = current_time
                        log_action("Left click (index + thumb)")

                    # Right click: Middle + Thumb pinch
                    if (
                        np.hypot(x_middle - x_thumb, y_middle - y_thumb)
                        < CLICK_DISTANCE_THRESHOLD
                        and (current_time - last_right_click) > COOLDOWN_TIME
                    ):
                        pyautogui.rightClick()
                        cv2.circle(img, (x_middle, y_middle), 15, (255, 0, 0), cv2.FILLED)
                        last_right_click = current_time
                        log_action("Right click (middle + thumb)")

                    # Scroll down: Ring + Thumb pinch
                    if (
                        np.hypot(x_ring - x_thumb, y_ring - y_thumb)
                        < CLICK_DISTANCE_THRESHOLD
                        and (current_time - last_scroll) > COOLDOWN_TIME
                    ):
                        pyautogui.scroll(-20)
                        cv2.circle(img, (x_ring, y_ring), 15, (0, 0, 255), cv2.FILLED)
                        last_scroll = current_time
                        log_action("Scroll down (ring + thumb)")

            cv2.imshow("Gesture Mouse", img)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                log_action("Program exited by user (ESC)")
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()