# DVA — Desktop Voice Assistant

A Python-based desktop voice assistant developed as a college project with the goal of creating a practical, interactive voice-controlled desktop assistant.

> **Status:** 🚧 Work in Progress

## 📌 About the Project

DVA (Desktop Voice Assistant) is a Python-based voice assistant designed to interact with the user through speech and perform useful desktop and web-related tasks.

The project is being developed as a college project and is continuously being improved with new features, better voice interaction, and improved reliability.

## ✨ Planned & Implemented Features

The project is being developed to support features such as:

* 🎙️ Voice-based interaction
* 🗣️ Speech-to-text recognition
* 🔊 Text-to-speech responses
* 👋 Wake-word activation
* 🖥️ Desktop application control
* 🌐 Website opening and searching
* 🔎 Google search
* 🌐 Firefox-based search
* 📅 Date and time information
* 🌤️ Weather information
* 🔊 System volume controls
* ☀️ Display brightness controls
* 📸 Screenshot functionality
* 💬 General conversation
* 🪟 Floating voice-assistant HUD / popup
* 📝 Assistant history and logging

> Some features may currently be under development or may change as the project evolves.

## 🛠️ Technologies Used

The project primarily uses:

* **Python**
* **Vosk** — Offline speech recognition
* **Text-to-Speech**
* **Tkinter** — Desktop interface / HUD
* **Windows system APIs and utilities**
* **Web browser integration**

Additional libraries and technologies may be added as development continues.

## 🎯 Project Goals

The main goals of DVA are to:

1. Create a functional desktop voice assistant using Python.
2. Enable offline speech recognition where possible.
3. Provide natural voice-based interaction.
4. Automate common desktop tasks.
5. Integrate useful web and system controls.
6. Create a simple and responsive user interface.
7. Learn practical concepts in Python, automation, speech processing, and software development.

## 📂 Project Structure

The project structure is currently under development.

A typical structure may look like:

```text
Desktop-Voice-Assistant/
│
├── main.py
├── assistant.py
├── config.json
├── requirements.txt
├── README.md
├── .gitignore
│
├── core/
├── services/
├── utils/
├── assets/
└── logs/
```

The final structure may change as the project develops.

## 🚀 Getting Started

### Prerequisites

Before running the project, make sure you have:

* Python 3.x
* A working microphone
* Windows operating system
* Required Python packages
* Required speech-recognition model files

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/Desktop-Voice-Assistant.git
```

Move into the project directory:

```bash
cd Desktop-Voice-Assistant
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Then configure the required settings and models before running the assistant.

> Installation instructions will be updated as the project reaches a more stable version.

## ▶️ Running the Assistant

Once the required dependencies and configuration are installed, run the main Python file:

```bash
python main.py
```

The exact startup command may change during development.

## 🎤 Speech Recognition

DVA is designed to use **Vosk** for offline speech recognition.

The speech-recognition component is intended to allow the assistant to process voice commands without requiring a constant internet connection for speech recognition.

## 🪟 User Interface

The project includes a lightweight floating HUD concept for displaying assistant status, such as:

* Listening
* Processing
* Responding
* Command execution

The interface is being developed to appear when required and disappear after the command has been processed.

## 🔐 Privacy

The project is designed with offline speech recognition in mind.

However, some features such as web searches, weather information, or online services may require an internet connection.

Do not store API keys, passwords, tokens, or other sensitive information directly in the repository.

## 🧪 Development Status

DVA is actively being developed.

Current development areas include:

* Improving speech recognition
* Improving voice responses
* Command routing
* Desktop automation
* HUD improvements
* Error handling
* Configuration management
* Logging and history
* Overall assistant reliability

## 🔮 Future Improvements

Possible future improvements include:

* More natural conversations
* Better wake-word detection
* Improved command understanding
* More desktop automation
* Better GUI/HUD animations
* Plugin or service architecture
* User preferences
* More system controls
* Better error recovery
* Improved logging
* Modular command system
* Additional language support

## 👨‍💻 Contributors

This project is being developed as a college project by:

* **Mohd Ammar Khan**
* **College Project Partner**

Additional contributors may be added as development continues.

## 📜 License

This project currently uses the MIT License.

See the `LICENSE` file for details.

---

⭐ If you find this project interesting, feel free to explore the repository as development continues.
