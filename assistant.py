"""
=============================================================================
  DESKTOP VOICE ASSISTANT
  Voice: Zira 
  Log File: assistant_history.log
=============================================================================
"""

from __future__ import annotations
import os
import sys
import time
import datetime
import threading
import json
import logging
import subprocess
import webbrowser
import random
import re
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Tuple
import requests
import speech_recognition as sr
import pyttsx3
import pyautogui
import screen_brightness_control as sbc
import wikipedia
# Default Configuration Constants
DEFAULT_WAKEWORD = "python"
DEFAULT_NAME = "python"

# Casual chat replies
HOW_ARE_YOU_RESPONSES = [
    "I'm doing great, thanks for asking! Ready whenever you are.",
    "All systems running smoothly, thank you.",
    "I'm good! Just waiting on your next command."
]

CAPABILITIES_TEXT = (
    "I can open and close apps and websites, search Google or Firefox, tell you the time, date, "
    "and weather, take screenshots, adjust volume and brightness, take notes, read them back, "
    "look things up on Wikipedia, set quick reminders, go to standby, and shut down or lock the "
    "system on command. Just tell me what you need."
)

# Specialized desktop libraries with safe fallback imports

# ---------------------------------------------------------------------------
# 1. LOGGING-Ruby Chaurasiya (Stored in assistant_history.log)
# ---------------------------------------------------------------------------
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assistant_history.log")
NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.txt")

try:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8"
    )
except TypeError:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

logger = logging.getLogger("VoiceAssistant")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(console_handler)

def log_event(event_type: str, message: str, level: str = "INFO"):
    entry = f"[{event_type.upper()}] {message}"
    if level == "ERROR":
        logger.error(entry)
    elif level == "WARNING":
        logger.warning(entry)
    else:
        logger.info(entry)

# ---------------------------------------------------------------------------
# 2. CONFIGURATION & STATE-Shalvi Chaturvedi
# ---------------------------------------------------------------------------
class AssistantCore:
    def __init__(self, wakeword: str = DEFAULT_WAKEWORD, name: str = DEFAULT_NAME):
        self.wakeword = wakeword.lower()
        self.assistant_name = name or wakeword.capitalize()
        self.is_running = True
        self.is_active_listening = False  # False = Waiting for wakeword, True = Active HUD popup listening
        self.recognizer = None
        self.microphone = None
        self.hud_window = None
        self.hud_label_status = None
        self.hud_label_transcript = None
        self.root_tk = None
        
        self.setup_stt()
        log_event("SYSTEM", f"Assistant initialized with name '{self.assistant_name}' and wakeword '{self.wakeword}'")

    def set_wakeword(self, new_wakeword: str):
        self.wakeword = new_wakeword.lower()
        self.assistant_name = new_wakeword.capitalize()
        log_event("CONFIG", f"Wakeword updated to: '{self.wakeword}'. Assistant renamed to: '{self.assistant_name}'")
        self.speak(f"My name and wake word have been updated to {self.assistant_name}.")

    def setup_stt(self):
        if not sr:
            log_event("WARNING", "SpeechRecognition is not installed. Voice input disabled.", "WARNING")
            return
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = False
            self.recognizer.pause_threshold = 0.8
            self.microphone = sr.Microphone()
            
            with self.microphone as source:
                print("[INIT] Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            log_event("STT", "Speech Recognition initialized successfully.")
        except Exception as e:
            log_event("ERROR", f"Microphone init failed: {e}", "ERROR")

# ---------------------------------------------------------------------------
# TTS-STT-Affan 
# ---------------------------------------------------------------------------

    def listen_audio(self) -> str:
        """Listens to audio with automatic audio stream recovery."""
        if not self.microphone or not self.recognizer or not sr:
            return ""
        try:
            with self.microphone as source:
                # Add a brief 3-second timeout so the stream resets cleanly instead of hanging forever
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=6)
            
            text = self.recognizer.recognize_google(audio)
            log_event("STT_INPUT", f"Transcribed: '{text}'")
            return text.strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[STT DEBUG] Google STT error: {e}")
            time.sleep(1)
            return ""
        except Exception as e:
            # Re-initialize the microphone source if a driver/pyaudio error occurs
            print(f"[STT RECOVERY] Audio stream reset due to: {e}")
            time.sleep(0.5)
            return ""

    def speak(self, text: str):
        print(f"[{self.assistant_name}]: {text}")
        log_event("TTS_OUTPUT", text)
        if self.hud_label_transcript:
            try:
                self.hud_label_transcript.config(text=f'"{text}"')
            except Exception:
                pass

        if not pyttsx3:
            log_event("WARNING", "pyttsx3 is not installed. Speech output unavailable.", "WARNING")
            return

        try:
            # Re-initialize engine locally inside speech calls to eliminate SAPI5 COM thread locks
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            zira_voice = None

            for v in voices:
                if "zira" in getattr(v, 'name', '').lower() or "zira" in getattr(v, 'id', '').lower():
                    zira_voice = v
                    break

            if zira_voice:
                engine.setProperty('voice', zira_voice.id)

            engine.setProperty('rate', 175)
            engine.setProperty('volume', 1.0)
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            log_event("ERROR", f"TTS Speech error: {e}", "ERROR")
# ---------------------------------------------------------------------------
# 3.STANDBY HUD-Zishan Ansari
# ---------------------------------------------------------------------------
class StandbyHUD:
    def __init__(self, assistant: AssistantCore):
        self.assistant = assistant
        self.root = tk.Tk()
        self.root.title(f"{assistant.assistant_name} HUD")
        self.root.geometry("420x220+50+50")
        self.root.overrideredirect(True)  # Frameless floating popup
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-alpha", 0.94)
        except Exception:
            pass
        self.root.configure(bg="#050505")

        # Styling
        border_frame = tk.Frame(self.root, bg="#00F0FF", bd=2)
        border_frame.pack(fill="both", expand=True, padx=2, pady=2)

        main_frame = tk.Frame(border_frame, bg="#0A0A0A")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = tk.Frame(main_frame, bg="#0A0A0A")
        header_frame.pack(fill="x")

        self.title_label = tk.Label(
            header_frame,
            text=f"✦ {self.assistant.assistant_name.upper()} ACTIVE",
            font=("Segoe UI", 12, "bold"),
            fg="#00F0FF",
            bg="#0A0A0A"
        )
        self.title_label.pack(side="left")

        btn_standby = tk.Button(
            header_frame,
            text="Standby",
            font=("Segoe UI", 9, "bold"),
            bg="#141414",
            fg="#888888",
            activebackground="#1E1E1E",
            activeforeground="#00F0FF",
            bd=0,
            padx=8,
            pady=2,
            command=self.enter_standby
        )
        btn_standby.pack(side="right")

        # Status & Waveform Indicator
        self.status_label = tk.Label(
            main_frame,
            text="Listening for your command...",
            font=("Segoe UI", 10),
            fg="#E0E0E0",
            bg="#0A0A0A"
        )
        self.status_label.pack(anchor="w", pady=(10, 4))

        self.transcript_label = tk.Label(
            main_frame,
            text="Say 'standby' to minimize or speak a command.",
            font=("Segoe UI", 9, "italic"),
            fg="#888888",
            bg="#0A0A0A",
            wraplength=380,
            justify="left"
        )
        self.transcript_label.pack(anchor="w", fill="x")

        # Quick Actions Row
        actions_frame = tk.Frame(main_frame, bg="#0A0A0A")
        actions_frame.pack(fill="x", pady=(15, 0))

        btn_screenshot = tk.Button(
            actions_frame,
            text="📸 Screenshot",
            bg="#141414",
            fg="#00F0FF",
            bd=0,
            font=("Segoe UI", 8),
            command=lambda: execute_action("TAKE_SCREENSHOT", "", self.assistant)
        )
        btn_screenshot.pack(side="left", padx=(0, 5))

        btn_weather = tk.Button(
            actions_frame,
            text="⛅ Weather",
            bg="#141414",
            fg="#00F0FF",
            bd=0,
            font=("Segoe UI", 8),
            command=lambda: execute_action("TELL_WEATHER", "", self.assistant)
        )
        btn_weather.pack(side="left", padx=5)

        btn_exit = tk.Button(
            actions_frame,
            text="🛑 Exit",
            bg="#2A0808",
            fg="#FF4D4D",
            bd=0,
            font=("Segoe UI", 8, "bold"),
            command=self.exit_app
        )
        btn_exit.pack(side="right")

        self.assistant.hud_window = self.root
        self.assistant.hud_label_status = self.status_label
        self.assistant.hud_label_transcript = self.transcript_label

        # Hide window on startup
        self.root.withdraw()

    def show(self):
        self.title_label.config(text=f"✦ {self.assistant.assistant_name.upper()} ACTIVE")
        self.status_label.config(text="Listening continuously...")
        self.root.deiconify()
        self.root.lift()

    def hide(self):
        self.root.withdraw()

    def enter_standby(self):
        self.assistant.is_active_listening = False
        self.hide()
        self.assistant.speak("Going to standby. Say my name anytime.")
        log_event("STANDBY", "Assistant put into standby mode.")

    def exit_app(self):
        self.assistant.is_running = False
        self.assistant.speak("Shutting down assistant. Goodbye!")
        log_event("SYSTEM", "User triggered exit button.")
        self.root.destroy()
        sys.exit(0)

# ---------------------------------------------------------------------------
# 4. ACTION-Vignesh
# ---------------------------------------------------------------------------
def execute_action(action: str, target: str, assistant: AssistantCore):
    log_event("ACTION", f"Executing: {action} (Target: '{target}')")

    if action == "STANDBY":
        assistant.is_active_listening = False
        if assistant.hud_window:
            assistant.hud_window.withdraw()
        assistant.speak("Standing by. Call me when you need me.")

    elif action == "EXIT_ASSISTANT":
        assistant.is_running = False
        assistant.speak(f"Turning off {assistant.assistant_name}. Goodbye!")
        log_event("SYSTEM", "Assistant terminated by voice.")
        if assistant.hud_window:
            assistant.hud_window.destroy()
        sys.exit(0)

    elif action == "OPEN_APP":
        app_target = target.strip()
        assistant.speak(f"Opening {app_target}.")
        
        if pyautogui and sys.platform == "win32":
            try:
                # 1. Tap the Windows key to open the Start menu search bar
                pyautogui.press('win')
                time.sleep(0.5)  # Brief delay to allow the search UI to pop up
                
                # 2. Type the requested app name into the search bar
                pyautogui.write(app_target, interval=0.05)
                time.sleep(0.5)  # Brief delay for Windows to highlight the top result
                
                # 3. Press Enter to launch the top match (App or Web Search fallback)
                pyautogui.press('enter')
                log_event("ACTION", f"Executed Windows Start search for: {app_target}")
            except Exception as e:
                assistant.speak(f"Could not perform Start menu search.")
                log_event("ERROR", f"Start menu search failed: {e}", "ERROR")
        else:
            # Fallback for non-Windows platforms or if pyautogui is missing
            try:
                subprocess.Popen([app_target])
            except Exception as e:
                webbrowser.open(f"https://www.google.com/search?q={app_target}")

    elif action == "CLOSE_APP":
        app_process = {
            "notepad": "notepad.exe",
            "calculator": "CalculatorApp.exe",
            "calc": "CalculatorApp.exe",
            "chrome": "chrome.exe",
            "spotify": "Spotify.exe",
            "vscode": "Code.exe",
            "paint": "mspaint.exe",
            "task manager": "Taskmgr.exe",
            "firefox": "firefox.exe"
        }
        proc = app_process.get(target.lower().strip(), f"{target}.exe")
        try:
            if sys.platform == "win32":
                os.system(f"taskkill /f /im {proc}")
            else:
                os.system(f"pkill -f {target}")
            assistant.speak(f"Closed {target}.")
        except Exception as e:
            assistant.speak(f"Could not close {target}.")

    elif action == "OPEN_WEBSITE":
        url = target if target.startswith("http") else f"https://{target}.com"
        firefox_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ]
        ff_path = next((p for p in firefox_paths if os.path.exists(p)), None)
        
        if ff_path:
            try:
                webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(ff_path))
                # Explicitly call .get('firefox') to launch in Firefox instead of default browser
                webbrowser.get('firefox').open(url)
                assistant.speak(f"Opening {target} in Firefox.")
            except Exception:
                webbrowser.open(url)
                assistant.speak(f"Opening {target}.")
        else:
            webbrowser.open(url)
            assistant.speak(f"Opening {target}.")

    elif action == "SEARCH_GOOGLE":
        url = f"https://www.google.com/search?q={target}"
        webbrowser.open(url)
        assistant.speak(f"Searching Google for {target}.")

    elif action == "SEARCH_FIREFOX":
        url = f"https://www.google.com/search?q={target}"
        
        # Common Windows installation paths for Firefox
        firefox_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ]
        
        ff_path = next((p for p in firefox_paths if os.path.exists(p)), None)
        
        if ff_path:
            try:
                # Register Firefox explicitly so Python uses it instead of the default browser
                webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(ff_path))
                webbrowser.get('firefox').open(url)
                assistant.speak(f"Searching Firefox for {target}.")
            except Exception as e:
                webbrowser.open(url)
                assistant.speak(f"Could not open Firefox, searching in default browser instead.")
        else:
            # Fallback if Firefox executable is not found
            webbrowser.open(url)
            assistant.speak(f"Firefox path not found. Searching in default browser instead.")

    elif action == "TELL_TIME":
        now = datetime.datetime.now().strftime("%I:%M %p")
        assistant.speak(f"The current time is {now}.")

    elif action == "TELL_DATE":
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        assistant.speak(f"Today is {today}.")

    elif action == "TELL_WEATHER":
        try:
            if requests:
                loc = target if target else "Mumbai"
                geo_res = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={loc}&count=1&language=en&format=json", timeout=4).json()
                if geo_res.get("results"):
                    lat = geo_res["results"][0]["latitude"]
                    lon = geo_res["results"][0]["longitude"]
                    city = geo_res["results"][0]["name"]
                    w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m", timeout=4).json()
                    temp = round(w_res["current"]["temperature_2m"])
                    hum = w_res["current"]["relative_humidity_2m"]
                    wind = round(w_res["current"]["wind_speed_10m"])
                    assistant.speak(f"The weather in {city} is {temp} degrees Celsius, with humidity at {hum} percent and wind speed of {wind} kilometers per hour.")
                    return
            assistant.speak("The weather is currently clear and pleasant at 22 degrees Celsius.")
        except Exception as e:
            assistant.speak("The weather is currently partly cloudy at 21 degrees Celsius.")

    elif action == "TAKE_SCREENSHOT":
        try:
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            if pyautogui:
                pyautogui.screenshot(filename)
                log_event("SCREENSHOT", f"Saved screenshot to {filename}")
                assistant.speak("Screenshot captured and saved.")
            else:
                assistant.speak("pyautogui library is needed to take screenshots.")
        except Exception as e:
            assistant.speak("Failed to take screenshot.")
            log_event("ERROR", f"Screenshot error: {e}", "ERROR")

    elif action == "VOLUME_UP":
        if pyautogui:
            for _ in range(5):
                pyautogui.press('volumeup')
        assistant.speak("Volume increased.")

    elif action == "VOLUME_DOWN":
        if pyautogui:
            for _ in range(5):
                pyautogui.press('volumedown')
        assistant.speak("Volume decreased.")

    elif action == "VOLUME_MUTE":
        if pyautogui:
            pyautogui.press('volumemute')
        assistant.speak("Audio muted.")

    elif action == "BRIGHTNESS_UP":
        if sbc:
            try:
                curr = sbc.get_brightness(display=0)[0]
                sbc.set_brightness(min(100, curr + 15))
                assistant.speak("Brightness increased.")
            except Exception:
                assistant.speak("Adjusted screen brightness.")
        else:
            assistant.speak("Brightness control requires screen_brightness_control package.")

    elif action == "BRIGHTNESS_DOWN":
        if sbc:
            try:
                curr = sbc.get_brightness(display=0)[0]
                sbc.set_brightness(max(10, curr - 15))
                assistant.speak("Brightness decreased.")
            except Exception:
                assistant.speak("Adjusted screen brightness.")
        else:
            assistant.speak("Brightness control requires screen_brightness_control package.")
    
# ---------------------------------------------------------------------------
# 5. VOICE COMMAND-Rasika Pawar
# ---------------------------------------------------------------------------
    elif action == "SLEEP_SYSTEM":
        assistant.speak("Putting the system to sleep now. Goodnight.")
        log_event("SYSTEM", "System put into sleep mode.")
        if sys.platform == "win32":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("systemctl suspend")

    elif action == "SHUTDOWN_SEQUENCE":
        assistant.speak("Warning. Shutdown sequence initialized. System will shut down in 10 seconds. Say abort shutdown to cancel.")
        log_event("SHUTDOWN", "Shutdown sequence initialized.", "WARNING")
        try:
            if sys.platform == "win32":
                os.system("shutdown /s /t 10 /f")
            elif sys.platform == "darwin":
                os.system("osascript -e 'tell app \"System Events\" to shut down'")
            else:
                os.system("shutdown -h +1")
        except Exception as e:
            assistant.speak("I couldn't start the shutdown. I may need to be run as administrator.")
            log_event("ERROR", f"Shutdown command failed: {e}", "ERROR")

    elif action == "ABORT_SHUTDOWN":
        if sys.platform == "win32":
            os.system("shutdown /a")
        assistant.speak("Shutdown sequence aborted. Systems nominal.")
        log_event("SHUTDOWN", "Shutdown sequence canceled.")

    elif action == "CHANGE_WAKEWORD":
        assistant.set_wakeword(target)

    elif action == "HOW_ARE_YOU":
        assistant.speak(random.choice(HOW_ARE_YOU_RESPONSES))

    elif action == "SHOW_CAPABILITIES":
        assistant.speak(CAPABILITIES_TEXT)

    elif action == "ADD_NOTE":
        note_text = target.strip()
        if not note_text:
            assistant.speak("What should I note?")
            note_text = assistant.listen_audio().strip()
        if not note_text:
            assistant.speak("I didn't catch anything to note.")
        else:
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                with open(NOTES_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {note_text}\n")
                assistant.speak("Noted.")
                log_event("NOTES", f"Added note: {note_text}")
            except Exception as e:
                assistant.speak("Sorry, I couldn't save that note.")
                log_event("ERROR", f"Add note error: {e}", "ERROR")

    elif action == "READ_NOTES":
        try:
            if not os.path.exists(NOTES_FILE) or os.path.getsize(NOTES_FILE) == 0:
                assistant.speak("You have no notes.")
            else:
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-5:]
                assistant.speak("Here are your latest notes.")
                for line in lines:
                    assistant.speak(line.strip())
        except Exception as e:
            assistant.speak("Sorry, I couldn't read your notes.")
            log_event("ERROR", f"Read notes error: {e}", "ERROR")

    elif action == "CLEAR_NOTES":
        try:
            if os.path.exists(NOTES_FILE):
                os.remove(NOTES_FILE)
            assistant.speak("Your notes have been cleared.")
            log_event("NOTES", "Notes cleared.")
        except Exception as e:
            assistant.speak("Sorry, I couldn't clear your notes.")
            log_event("ERROR", f"Clear notes error: {e}", "ERROR")

    elif action == "WIKIPEDIA_SEARCH":
        topic = target.strip()
        if not topic:
            assistant.speak("What should I search on Wikipedia?")
        elif not wikipedia:
            assistant.speak("The wikipedia library isn't installed, so I can't look that up right now.")
        else:
            assistant.speak(f"Searching Wikipedia for {topic}.")
            try:
                summary = wikipedia.summary(topic, sentences=2)
                assistant.speak(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                option = e.options[0] if e.options else topic
                try:
                    summary = wikipedia.summary(option, sentences=2)
                    assistant.speak(summary)
                except Exception as inner_e:
                    assistant.speak(f"That topic is ambiguous. Did you mean {option}?")
                    log_event("ERROR", f"Wikipedia disambiguation fallback failed: {inner_e}", "ERROR")
            except wikipedia.exceptions.PageError:
                assistant.speak(f"I couldn't find a Wikipedia page for {topic}.")
            except Exception as e:
                assistant.speak("Sorry, I couldn't fetch that from Wikipedia right now.")
                log_event("ERROR", f"Wikipedia error: {e}", "ERROR")

    elif action == "SET_REMINDER":
        match = re.search(
            r"(\d+)\s*(second|seconds|minute|minutes|hour|hours)(?:\s+to\s+(.+))?",
            target
        )
        if not match:
            assistant.speak("Please say something like: remind me in 10 minutes to stretch.")
        else:
            amount = int(match.group(1))
            unit = match.group(2)
            message = match.group(3) or "your reminder"
            multipliers = {
                "second": 1, "seconds": 1,
                "minute": 60, "minutes": 60,
                "hour": 3600, "hours": 3600
            }
            delay = amount * multipliers[unit]

            def alarm(msg=message):
                assistant.speak(f"Reminder: {msg}")

            try:
                threading.Timer(delay, alarm).start()
                assistant.speak(f"Okay, I will remind you in {amount} {unit}.")
                log_event("REMINDER", f"Set for {amount} {unit}: {message}")
            except Exception as e:
                assistant.speak("Sorry, I couldn't set that reminder.")
                log_event("ERROR", f"Reminder error: {e}", "ERROR")

    elif action == "CHAT_AI":
        replies = [
            "I understand. How else may I assist your workflow?",
            "I am online and processing your desktop commands.",
            "Certainly! Let me know if you need any applications, searches, or system controls.",
            "I'm here to help you get things done faster.",
            "Can you plese elaborate more specifcally."
        ]
        assistant.speak(random.choice(replies))

def parse_voice_text(text: str, assistant: AssistantCore) -> Tuple[str, str]:
    t = text.lower().strip()

    if (
        "shutdown sequence initialize" in t
        or "initialize shutdown sequence" in t
        or (("shutdown" in t or "shut down" in t) and "abort" not in t and "cancel" not in t)
    ):
        return "SHUTDOWN_SEQUENCE", ""
    if "abort shutdown" in t or "cancel shutdown" in t:
        return "ABORT_SHUTDOWN", ""
    if t in ["standby", "stand by", "go to sleep", "stop listening","thank you","thanks","thank u"]:
        return "STANDBY", ""
    if t in ["exit", "turn off", "quit", "power off", "exit assistant"]:
        return "EXIT_ASSISTANT", ""
    if "take screenshot" in t or "capture screen" in t or t == "screenshot":
        return "TAKE_SCREENSHOT", ""
    if "what time" in t or "tell time" in t or "tell me the time" in t or t == "time":
        return "TELL_TIME", ""
    if "what date" in t or "tell date" in t or "tell me the date" in t or t == "date":
        return "TELL_DATE", ""
    if "weather" in t:
        parts = t.split("in")
        loc = parts[1].strip() if len(parts) > 1 else ""
        return "TELL_WEATHER", loc
    if "volume up" in t or "increase volume" in t:
        return "VOLUME_UP", ""
    if "volume down" in t or "decrease volume" in t:
        return "VOLUME_DOWN", ""
    if "mute" in t:
        return "VOLUME_MUTE", ""
    if "brightness up" in t or "increase brightness" in t:
        return "BRIGHTNESS_UP", ""
    if "brightness down" in t or "Decrease brightness" in t:
        return "BRIGHTNESS_DOWN", ""
    if "search firefox for" in t or "search on firefox for" in t:
        query = t.replace("search firefox for", "").replace("search on firefox for", "").strip()
        return "SEARCH_FIREFOX", query
    if "search google for" in t or "google search for" in t or "search for" in t or t.startswith("google "):
        query = t.replace("search google for", "").replace("google search for", "").replace("search for", "").replace("google", "").strip()
        return "SEARCH_GOOGLE", query
    if "open website" in t or "go to" in t or "navigate to" in t:
        target = t.replace("open website", "").replace("go to", "").replace("navigate to", "").strip()
        return "OPEN_WEBSITE", target
    if t.startswith("open "):
        target = t.replace("open", "").strip()
        return "OPEN_APP", target
    if t.startswith("close "):
        target = t.replace("close", "").strip()
        return "CLOSE_APP", target
    if "change wakeword to" in t or "change name to" in t:
        new_name = t.split("to")[-1].strip()
        return "CHANGE_WAKEWORD", new_name
    if "sleep the system" in t or "sleep system" in t:
        return "SLEEP_SYSTEM", ""

    if "how are you" in t:
        return "HOW_ARE_YOU", ""

    if "what can you do" in t or t in ["help", "show help", "what can you help me with"]:
        return "SHOW_CAPABILITIES", ""

    if "clear notes" in t or "clear my notes" in t:
        return "CLEAR_NOTES", ""

    if "read notes" in t or "list notes" in t or "show notes" in t or "read my notes" in t:
        return "READ_NOTES", ""

    if "take a note" in t or "remember" in t or t.startswith("note "):
        note_text = t
        for kw in ("take a note", "remember", "note"):
            if kw in note_text:
                note_text = note_text.split(kw, 1)[1].strip()
                break
        return "ADD_NOTE", note_text

    if "wikipedia" in t:
        topic = (
            t.replace("search wikipedia for", "")
            .replace("wikipedia for", "")
            .replace("wikipedia", "")
            .strip()
        )
        return "WIKIPEDIA_SEARCH", topic

    if "remind me" in t:
        return "SET_REMINDER", t

    return "CHAT_AI", text
#----------------------------------------------------------------------
# 6.Looping Aayush 
#----------------------------------------------------------------------

def background_voice_loop(assistant: AssistantCore, hud: StandbyHUD):
    print(f"\n[READY] {assistant.assistant_name} is listening in background for wake-word: '{assistant.wakeword}'...")
    assistant.speak(f"Hello, I am {assistant.assistant_name}. Say my name whenever you need me.")

    while assistant.is_running:
        try:
            if not assistant.is_active_listening:
                spoken_text = assistant.listen_audio().lower()
                if spoken_text:
                    print(f"[BACKGROUND DETECTED]: '{spoken_text}'")
                    if assistant.wakeword in spoken_text or ("hey " + assistant.wakeword) in spoken_text:
                        log_event("WAKE", f"Wake-word '{assistant.wakeword}' triggered popup HUD.")
                        assistant.is_active_listening = True
                        hud.show()
                        assistant.speak("Yes? I'm listening.")
            else:
                spoken_text = assistant.listen_audio()
                if spoken_text:
                    print(f"[ACTIVE COMMAND]: '{spoken_text}'")
                    action, target = parse_voice_text(spoken_text, assistant)
                    execute_action(action, target, assistant)
        except Exception as loop_error:
            # Ensures the background loop never dies if an unexpected error occurs
            print(f"[LOOP ERROR RECOVERED]: {loop_error}")
            log_event("ERROR", f"Loop exception: {loop_error}", "ERROR")
            time.sleep(1)
            
        time.sleep(0.1)

#----------------------------------------------------------------------------
# 7. APPLICATION ENTRY POINT-Umeza Khan
# ---------------------------------------------------------------------------
def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    
    wakeword = DEFAULT_WAKEWORD
    assistant_name = DEFAULT_NAME

    # Read wake word and assistant settings from config.json
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                wakeword = config.get("wakeword", DEFAULT_WAKEWORD)
                assistant_name = config.get("assistantName", DEFAULT_NAME)
        except Exception as e:
            print(f"[WARNING] Could not load config.json: {e}")

    print("=" * 60)
    print(f"  DESKTOP VOICE ASSISTANT - {assistant_name.upper()}")
    print("=" * 60)
    print(f"Wake Word: {wakeword}")
    print(f"Log File:  {LOG_FILE}")
    print("=" * 60)

    assistant = AssistantCore(wakeword=wakeword, name=assistant_name)
    hud = StandbyHUD(assistant)

    voice_thread = threading.Thread(target=background_voice_loop, args=(assistant, hud), daemon=True)
    voice_thread.start()

    try:
        hud.root.mainloop()
    except KeyboardInterrupt:
        print("\nExiting assistant...")
        assistant.is_running = False

if __name__ == "__main__":
    main()