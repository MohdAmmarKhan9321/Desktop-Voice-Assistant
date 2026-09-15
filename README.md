# Desktop Voice Assistant (DVA)

A Python-based desktop voice assistant that can control desktop applications, websites, system functions, and perform voice-based tasks.

## Features

* 🎙️ Voice commands
* 🗣️ Zira text-to-speech voice
* 🖥️ Open and close desktop applications
* 🌐 Open websites
* 🔎 Google and Firefox search
* 🕐 Time and date
* 🌦️ Weather information
* 📸 Take screenshots
* 🔊 Volume control
* 💡 Brightness control
* 📝 Notes
* ⏰ Quick reminders
* 📖 Wikipedia search
* 💤 Standby mode
* ⚙️ Custom wake word and assistant name
* 🪟 Floating HUD interface
* 📋 Command history logging

## Technologies

* Python
* Tkinter
* SpeechRecognition
* Pyttsx3
* PyAutoGUI
* Screen Brightness Control
* Requests
* Wikipedia

## Installation

Install the required libraries:

```bash
pip install SpeechRecognition pyttsx3 pyautogui screen-brightness-control requests wikipedia
```

Run the assistant:

```bash
python assistant.py
```

## Commands

| Command                | Example                        |
| ---------------------- | ------------------------------ |
| Open application       | `open notepad`                 |
| Close application      | `close notepad`                |
| Open website           | `open youtube`                 |
| Google search          | `google search Python`         |
| Firefox search         | `firefox search latest news`   |
| Time                   | `what is the time`             |
| Date                   | `what is today's date`         |
| Weather                | `what is the weather`          |
| Screenshot             | `take screenshot`              |
| Volume up              | `volume up`                    |
| Volume down            | `volume down`                  |
| Mute                   | `mute volume`                  |
| Brightness up          | `brightness up`                |
| Brightness down        | `brightness down`              |
| Take note              | `take a note`                  |
| Read notes             | `read my notes`                |
| Wikipedia              | `wikipedia Python`             |
| Standby                | `standby`                      |
| Sleep                  | `sleep computer`               |
| Shutdown               | `shutdown sequence initialize` |
| Change wake word       | `change wake word`             |
| Assistant capabilities | `what can you do`              |
