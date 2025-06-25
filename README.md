# drowsiness-detection-system

\<p align="center"\>
\<img src="image\_0eb5c4.png" alt="Project GUI Screenshot"/\>
\</p\>

A real-time drowsiness detection system built with Python, OpenCV, and Dlib. This application monitors a user's face via webcam to detect signs of fatigue, such as eye closure and yawning, and triggers an alarm to prevent accidents.

[](https://opensource.org/licenses/MIT)
[](https://www.python.org/)

-----

## 🌟 Features

  * **Real-Time Face & Landmark Detection**: Utilizes dlib's 68-point facial landmark predictor to accurately track facial features in real-time.
  * **Eye Aspect Ratio (EAR) Monitoring**: Calculates the EAR to precisely detect the level of eye-opening and identify prolonged closure.
  * **Yawn Detection**: Measures the Mouth Aspect Ratio (MAR) to detect when the user is yawning, another key indicator of drowsiness.
  * **Interactive GUI**: A user-friendly interface built with Tkinter that displays the video feed, live detection metrics (EAR & MAR), and status updates.
  * **Configurable Thresholds**: Allows for real-time adjustment of EAR and Yawn detection sensitivity via sliders in the control panel.
  * **Audible & Visual Alerts**: Provides immediate on-screen warnings and plays an alarm sound to alert the user when drowsiness is detected.

-----

## ⚙️ How It Works

The system processes video from a webcam frame by frame. For each frame, it performs the following steps:

1.  **Face Detection**: Locates the user's face in the frame using dlib's frontal face detector.

2.  **Facial Landmark Prediction**: Identifies 68 specific points on the face (eyes, mouth, nose, etc.).

3.  **Ratio Calculations**:

      * **Eye Aspect Ratio (EAR)**: This ratio is calculated to determine if the eyes are closed. The formula is:

        $$
        $$$$EAR = \\frac{||p\_2 - p\_6|| + ||p\_3 - p\_5||}{2 \\cdot ||p\_1 - p\_4||}

        $$
        $$$$A low EAR value that persists for a certain number of frames indicates drowsiness.

      * **Mouth Aspect Ratio (MAR)**: This ratio is calculated to detect yawns. A high MAR value suggests a yawn.

4.  **Drowsiness Assessment**: If the EAR drops below a defined threshold or the MAR exceeds its threshold, the system increments a counter. If these conditions persist, an alarm is triggered.

-----

## 📂 Project Structure

```
drowsiness-detection-system/
│
├── drowsiness_detector.py      # Core class for detection logic
├── drowsiness_gui.py           # Main application with the Tkinter GUI
├── create_alarm.py             # Utility script to generate the alarm sound
├── alarm.wav                   # The alarm sound file
│
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── LICENSE                     # MIT License file
├── .gitignore                  # Files to be ignored by Git
│
└── shape_predictor_68_face_landmarks.dat  # Pre-trained dlib model
```

-----

## 🛠️ Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/drowsiness-detection-system.git
    cd drowsiness-detection-system
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

    > **Note**: `dlib` can be tricky to install. You may need to have `CMake` and a C++ compiler installed on your system first. For Windows, this means installing Visual Studio with C++ build tools.

4.  **Download the Facial Landmark Predictor:**
    Make sure the `shape_predictor_68_face_landmarks.dat` file is present in the root directory of the project. If not, you can download it from [dlib's official website](https://www.google.com/search?q=http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) and extract it.

-----

## 🚀 Usage

To run the application, execute the GUI script from your terminal:

```bash
python drowsiness_gui.py
```

The system will start, open your webcam, and begin monitoring. To stop the program, you can either use the "Stop Detection" button in the GUI or press `q` while the video window is active.

-----

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
