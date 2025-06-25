import cv2
import numpy as np
import dlib
from scipy.spatial import distance
import time
import threading
import pygame

class DrowsinessDetector:
    def __init__(self):
        # Initialize dlib's face detector and facial landmark predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        
        # Initialize pygame for alarm sound
        pygame.mixer.init()
        self.alarm_sound = pygame.mixer.Sound('alarm.wav')
        
        # Constants for drowsiness detection - made more sensitive
        self.EAR_THRESHOLD = 0.15  # Lowered threshold for eye detection
        self.YAWN_THRESHOLD = 0.35    # Lowered threshold for yawn detection
        self.CONSECUTIVE_FRAMES = 3  # Reduced frames for faster detection
        self.BLINK_THRESHOLD = 0.15  # Threshold for blink detection
        
        # Initialize counters and state
        self.eye_counter = 0
        self.yawn_counter = 0
        self.blink_counter = 0
        self.alarm_on = False
        self.last_ear = 1.0
        self.blink_detected = False
        self.last_mar = 0.0  # Track last MAR value
        self.alarm_thread = None
        
    def calculate_ear(self, eye_points):
        """Calculate Eye Aspect Ratio with improved accuracy"""
        try:
            # Calculate vertical distances
            A = distance.euclidean(eye_points[1], eye_points[5])
            B = distance.euclidean(eye_points[2], eye_points[4])
            # Calculate horizontal distance
            C = distance.euclidean(eye_points[0], eye_points[3])
            # Calculate EAR
            ear = (A + B) / (2.0 * C)
            return ear
        except Exception as e:
            print(f"Error calculating EAR: {e}")
            return 1.0
    
    def calculate_yawn(self, mouth_points):
        """Calculate mouth aspect ratio for yawn detection with improved accuracy"""
        try:
            # Calculate vertical distances
            A = distance.euclidean(mouth_points[13], mouth_points[19])
            B = distance.euclidean(mouth_points[14], mouth_points[18])
            C = distance.euclidean(mouth_points[15], mouth_points[17])
            # Calculate horizontal distance
            D = distance.euclidean(mouth_points[12], mouth_points[16])
            # Calculate MAR
            mar = (A + B + C) / (2.0 * D)
            return mar
        except Exception as e:
            print(f"Error calculating MAR: {e}")
            return 0.0
    
    def detect_blink(self, current_ear):
        """Detect if a blink occurred"""
        if current_ear < self.BLINK_THRESHOLD and self.last_ear >= self.BLINK_THRESHOLD:
            self.blink_detected = True
            return True
        self.blink_detected = False
        return False
    
    def detect_yawn(self, current_mar):
        """Detect if a yawn occurred"""
        # More sensitive yawn detection
        if current_mar > self.YAWN_THRESHOLD:
            return True
        return False
    
    def play_alarm(self):
        """Play alarm sound in a separate thread"""
        while self.alarm_on:
            self.alarm_sound.play()
            time.sleep(1)
            
    def start_alarm(self):
        """Start the alarm if it's not already running"""
        if not self.alarm_on:
            self.alarm_on = True
            self.alarm_thread = threading.Thread(target=self.play_alarm)
            self.alarm_thread.daemon = True
            self.alarm_thread.start()
            
    def stop_alarm(self):
        """Stop the alarm"""
        self.alarm_on = False
        if self.alarm_thread:
            self.alarm_thread.join(timeout=1)
    
    def get_detection_status(self, ear, mar):
        """Get detailed detection status"""
        status = {
            'eye_status': 'Normal',
            'yawn_status': 'Normal',
            'blink_detected': False,
            'yawn_detected': False,
            'drowsiness_level': 0,
            'ear_value': ear,
            'mar_value': mar
        }
        
        # Check for blink
        if self.detect_blink(ear):
            status['blink_detected'] = True
            self.blink_counter += 1
        else:
            self.blink_counter = max(0, self.blink_counter - 1)
        
        # Check for yawn with more sensitive detection
        if self.detect_yawn(mar):
            status['yawn_detected'] = True
            status['yawn_status'] = 'Yawning'
            self.yawn_counter += 1
        else:
            self.yawn_counter = max(0, self.yawn_counter - 1)
        
        # Check for drowsiness based on both eye closure and yawns
        if ear < self.EAR_THRESHOLD:
            self.eye_counter += 1
            if self.eye_counter >= self.CONSECUTIVE_FRAMES:
                status['eye_status'] = 'Drowsy'
                status['drowsiness_level'] = 1
        else:
            self.eye_counter = 0
        
        # Update drowsiness level based on both yawns and eye closure
        if self.yawn_counter >= self.CONSECUTIVE_FRAMES or self.eye_counter >= self.CONSECUTIVE_FRAMES:
            status['drowsiness_level'] = 1
            self.start_alarm()
        else:
            self.stop_alarm()
        
        # Update last values
        self.last_ear = ear
        self.last_mar = mar
        
        return status
    
    def detect_drowsiness(self):
        """Main function to detect drowsiness"""
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            
            for face in faces:
                landmarks = self.predictor(gray, face)
                landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])
                
                # Get eye landmarks
                left_eye = landmarks[36:42]
                right_eye = landmarks[42:48]
                
                # Calculate EAR for both eyes
                left_ear = self.calculate_ear(left_eye)
                right_ear = self.calculate_ear(right_eye)
                ear = (left_ear + right_ear) / 2.0
                
                # Get mouth landmarks
                mouth = landmarks[48:68]
                mar = self.calculate_yawn(mouth)
                
                # Get detection status
                status = self.get_detection_status(ear, mar)
                
                # Draw landmarks
                for (x, y) in landmarks:
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                
                # Add visual feedback for yawn detection
                if status['yawn_detected']:
                    cv2.putText(frame, "YAWNING!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    # Draw rectangle around mouth
                    mouth_points = landmarks[48:68]
                    x_coords = [p[0] for p in mouth_points]
                    y_coords = [p[1] for p in mouth_points]
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    cv2.rectangle(frame, (x_min-10, y_min-10), (x_max+10, y_max+10), (0, 0, 255), 2)
                
                # Add visual feedback for eye closure
                if status['eye_status'] == 'Drowsy':
                    cv2.putText(frame, "DROWSY EYES!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    # Draw rectangles around eyes
                    left_eye_points = landmarks[36:42]
                    right_eye_points = landmarks[42:48]
                    
                    for eye_points in [left_eye_points, right_eye_points]:
                        x_coords = [p[0] for p in eye_points]
                        y_coords = [p[1] for p in eye_points]
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        cv2.rectangle(frame, (x_min-5, y_min-5), (x_max+5, y_max+5), (0, 0, 255), 2)
                
                # Display EAR and MAR values
                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"MAR: {mar:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display alarm status
                if self.alarm_on:
                    cv2.putText(frame, "ALARM ACTIVE!", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display the frame
            cv2.imshow("Drowsiness Detection", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_alarm()  # Ensure alarm is stopped when quitting
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = DrowsinessDetector()
    detector.detect_drowsiness()