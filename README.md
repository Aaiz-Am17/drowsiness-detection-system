# Drowsiness Detection System

A real-time drowsiness detection system using computer vision and facial landmarks. The system monitors eye closure and yawning to detect signs of drowsiness and alerts the user with visual and audio warnings.

## Features

- Real-time face detection
- Eye closure monitoring
- Yawning detection
- Audio and visual alerts
- Facial landmark tracking

## Requirements

- Python 3.x
- OpenCV
- dlib
- NumPy
- SciPy
- Pygame

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/drowsiness_detection.git
cd drowsiness_detection
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Download the facial landmark predictor:
```bash
# The shape_predictor_68_face_landmarks.dat file should be in the project directory
```

## Usage

1. Run the drowsiness detector:
```bash
python drowsiness_detector.py
```

2. The system will:
   - Open your webcam
   - Track your facial landmarks
   - Monitor for signs of drowsiness
   - Alert you with sound and visual warnings when drowsiness is detected

3. To exit the program, press 'q' on your keyboard

## How it Works

The system uses dlib's facial landmark detector to track 68 points on your face. It calculates:
- Eye Aspect Ratio (EAR) to detect eye closure
- Mouth Aspect Ratio (MAR) to detect yawning

When either of these metrics exceeds their respective thresholds for a certain duration, the system triggers an alert.

## License

MIT License
