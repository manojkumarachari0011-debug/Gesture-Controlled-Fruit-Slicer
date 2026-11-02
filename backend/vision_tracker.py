import cv2
import mediapipe as mp

class VisionTracker:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        
        # NEW: Stores the live video frame so the DisplayManager can show your face
        self.current_frame = None 

    def get_hand_position(self, screen_w, screen_h):
        ret, frame = self.cap.read()
        if not ret: return None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Save the frame for the picture-in-picture UI
        self.current_frame = rgb_frame 

        results = self.hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm = hand_landmarks.landmark[8]
                x = int(lm.x * screen_w)
                y = int(lm.y * screen_h)
                return (x, y)
        return None

    def release(self):
        self.cap.release()