# 🍎 Gesture-Controlled Fruit Slicer ("Fruit Ninja" Arcade Game)

A real-time, gesture-controlled arcade slicing game built in Python as a final-year Bachelor of Computer Applications (BCA) project. Players use their index finger via live webcam tracking to slice flying fruits, avoid bombs, trigger dynamic score multipliers, and manage persistent user profiles.

---

## 🚀 Key Features

* **Computer Vision Tracking:** Utilizes Google MediaPipe and OpenCV to track 21 3D hand landmarks in real-time, mapping the user's index finger directly to smooth Pygame blade coordinates.
* **Modular Software Architecture:** Built with a clean separation of concerns:
  * `main.py`: Central controller managing state machines, event loops, and game states.
  * `auth_manager.py`: Handles user authentication, SHA-256 password hashing, and persistent SQLite database sessions.
  * `vision_tracker.py`: Captures webcam feeds and performs landmark coordinate extraction.
  * `physics_engine.py`: Manages fruit trajectory, gravity, randomized spawns, and 2D Euclidean collision detection.
  * `display_manager.py`: Handles Pygame asset rendering, particle splash effects, UI dashboard panels, and the live Picture-in-Picture (PIP) camera feed.
* **Database & Multi-User Support:** Implements a relational SQLite database (`game_users.db`) featuring secure password hashing (`hashlib`), unique user profiles, high-score tracking, and full historical match logging.
* **Interactive Dashboard:** Includes settings to toggle BGM/SFX volume, enable/disable the live PIP camera feed, view career statistics, and review full match history grids.

---

## 🛠️ Tech Stack & Libraries

* **Programming Language:** Python 3.11[cite: 1]
* **Frontend / Rendering:** Pygame[cite: 1]
* **Computer Vision / Tracking:** OpenCV, Google MediaPipe[cite: 1]
* **Data Storage:** SQLite3[cite: 1]
* **Packaging:** PyInstaller (for standalone `.exe` deployment)[cite: 1]

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/manojkumarachari0011-debug/Gesture-Controlled-Fruit-Slicer.git](https://github.com/manojkumarachari0011-debug/Gesture-Controlled-Fruit-Slicer.git)
   cd Gesture-Controlled-Fruit-Slicer

   ## How to Play
1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
3.
```bash
   python main.py
