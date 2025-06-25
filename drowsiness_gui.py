import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
from drowsiness_detector import DrowsinessDetector
import numpy as np
import time

class DrowsinessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drowsiness Detection System")
        self.root.geometry("1200x800")
        
        # Initialize the drowsiness detector
        self.detector = DrowsinessDetector()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create video frame
        self.video_frame = ttk.LabelFrame(self.main_frame, text="Video Feed")
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create video label
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Create control panel
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Control Panel")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Add status indicators
        self.status_frame = ttk.LabelFrame(self.control_frame, text="Status")
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Eye status with value
        self.eye_status_frame = ttk.Frame(self.status_frame)
        self.eye_status_frame.pack(fill=tk.X, padx=5, pady=2)
        self.eye_status = ttk.Label(self.eye_status_frame, text="Eye Status: Normal")
        self.eye_status.pack(side=tk.LEFT)
        self.ear_value = ttk.Label(self.eye_status_frame, text="EAR: 0.0")
        self.ear_value.pack(side=tk.RIGHT)
        
        # Yawn status with value
        self.yawn_status_frame = ttk.Frame(self.status_frame)
        self.yawn_status_frame.pack(fill=tk.X, padx=5, pady=2)
        self.yawn_status = ttk.Label(self.yawn_status_frame, text="Yawn Status: Normal")
        self.yawn_status.pack(side=tk.LEFT)
        self.mar_value = ttk.Label(self.yawn_status_frame, text="MAR: 0.0")
        self.mar_value.pack(side=tk.RIGHT)
        
        # Blink counter
        self.blink_frame = ttk.Frame(self.status_frame)
        self.blink_frame.pack(fill=tk.X, padx=5, pady=2)
        self.blink_status = ttk.Label(self.blink_frame, text="Blink Status: No Blink")
        self.blink_status.pack(side=tk.LEFT)
        self.blink_counter = ttk.Label(self.blink_frame, text="Blink Count: 0")
        self.blink_counter.pack(side=tk.RIGHT)
        
        # Alarm status
        self.alarm_frame = ttk.Frame(self.status_frame)
        self.alarm_frame.pack(fill=tk.X, padx=5, pady=2)
        self.alarm_status = ttk.Label(self.alarm_frame, text="Alarm Status: Off")
        self.alarm_status.pack(side=tk.LEFT)
        
        # Add threshold controls
        self.threshold_frame = ttk.LabelFrame(self.control_frame, text="Thresholds")
        self.threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # EAR threshold
        ttk.Label(self.threshold_frame, text="EAR Threshold:").pack(fill=tk.X, padx=5, pady=2)
        self.ear_threshold = ttk.Scale(self.threshold_frame, from_=0.1, to=0.4, 
                                     orient=tk.HORIZONTAL, value=self.detector.EAR_THRESHOLD)
        self.ear_threshold.pack(fill=tk.X, padx=5, pady=2)
        
        # Yawn threshold
        ttk.Label(self.threshold_frame, text="Yawn Threshold:").pack(fill=tk.X, padx=5, pady=2)
        self.yawn_threshold = ttk.Scale(self.threshold_frame, from_=1, to=30, 
                                      orient=tk.HORIZONTAL, value=self.detector.YAWN_THRESHOLD)
        self.yawn_threshold.pack(fill=tk.X, padx=5, pady=2)
        
        # Add control buttons
        self.button_frame = ttk.Frame(self.control_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(self.button_frame, text="Start Detection", 
                                     command=self.start_detection)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_button = ttk.Button(self.button_frame, text="Stop Detection", 
                                    command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add alarm control
        self.alarm_button = ttk.Button(self.button_frame, text="Toggle Alarm", 
                                     command=self.toggle_alarm)
        self.alarm_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add debug mode toggle
        self.debug_var = tk.BooleanVar(value=True)
        self.debug_check = ttk.Checkbutton(self.button_frame, text="Debug Mode", 
                                         variable=self.debug_var)
        self.debug_check.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Initialize variables
        self.is_running = False
        self.cap = None
        self.update_thread = None
        self.blink_count = 0
        self.last_blink_time = time.time()
        self.alarm_enabled = True
        
    def toggle_alarm(self):
        self.alarm_enabled = not self.alarm_enabled
        if not self.alarm_enabled:
            self.detector.alarm_on = False
            self.alarm_status.config(text="Alarm Status: Off")
        else:
            self.alarm_status.config(text="Alarm Status: On")
        
    def start_detection(self):
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.cap = cv2.VideoCapture(0)
        self.update_thread = threading.Thread(target=self.update_frame)
        self.update_thread.start()
        
    def stop_detection(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.cap is not None:
            self.cap.release()
        self.detector.alarm_on = False
        
    def update_frame(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Update thresholds
            self.detector.EAR_THRESHOLD = self.ear_threshold.get()
            self.detector.YAWN_THRESHOLD = self.yawn_threshold.get()
            
            # Process frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detector(gray)
            
            if len(faces) == 0:
                cv2.putText(frame, "No Face Detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            for face in faces:
                landmarks = self.detector.predictor(gray, face)
                landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])
                
                # Get eye landmarks
                left_eye = landmarks[36:42]
                right_eye = landmarks[42:48]
                
                # Calculate EAR for both eyes
                left_ear = self.detector.calculate_ear(left_eye)
                right_ear = self.detector.calculate_ear(right_eye)
                ear = (left_ear + right_ear) / 2.0
                
                # Get mouth landmarks
                mouth = landmarks[48:68]
                mar = self.detector.calculate_yawn(mouth)
                
                # Get detection status
                status = self.detector.get_detection_status(ear, mar)
                
                # Update status labels
                self.eye_status.config(text=f"Eye Status: {status['eye_status']}")
                self.yawn_status.config(text=f"Yawn Status: {status['yawn_status']}")
                
                # Update values
                self.ear_value.config(text=f"EAR: {ear:.3f}")
                self.mar_value.config(text=f"MAR: {mar:.3f}")
                
                # Update blink status
                if status['blink_detected']:
                    current_time = time.time()
                    if current_time - self.last_blink_time > 0.5:  # Debounce blinks
                        self.blink_count += 1
                        self.last_blink_time = current_time
                    self.blink_status.config(text="Blink Status: Blink Detected")
                else:
                    self.blink_status.config(text="Blink Status: No Blink")
                
                self.blink_counter.config(text=f"Blink Count: {self.blink_count}")
                
                # Handle alarm
                if (status['drowsiness_level'] > 0 or status['yawn_detected']) and self.alarm_enabled:
                    if not self.detector.alarm_on:
                        self.detector.alarm_on = True
                        threading.Thread(target=self.detector.play_alarm).start()
                        self.alarm_status.config(text="Alarm Status: Active")
                else:
                    self.detector.alarm_on = False
                    if self.alarm_enabled:
                        self.alarm_status.config(text="Alarm Status: On")
                
                # Draw landmarks
                for (x, y) in landmarks:
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                
                # Draw eye and mouth regions
                if self.debug_var.get():
                    # Draw eye regions
                    cv2.rectangle(frame, (min(left_eye[:, 0]), min(left_eye[:, 1])),
                                (max(left_eye[:, 0]), max(left_eye[:, 1])), (0, 255, 0), 1)
                    cv2.rectangle(frame, (min(right_eye[:, 0]), min(right_eye[:, 1])),
                                (max(right_eye[:, 0]), max(right_eye[:, 1])), (0, 255, 0), 1)
                    
                    # Draw mouth region
                    cv2.rectangle(frame, (min(mouth[:, 0]), min(mouth[:, 1])),
                                (max(mouth[:, 0]), max(mouth[:, 1])), (0, 255, 0), 1)
                
                # Add status text to frame
                cv2.putText(frame, f"EAR: {ear:.3f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"MAR: {mar:.3f}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Add alarm status to frame
                if self.detector.alarm_on:
                    cv2.putText(frame, "ALARM ACTIVE!", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Add yawn detection status
                if status['yawn_detected']:
                    cv2.putText(frame, "YAWN DETECTED!", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Convert frame to PhotoImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 600))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            
            # Update video label
            self.video_label.config(image=photo)
            self.video_label.image = photo
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrowsinessGUI(root)
    app.run() 