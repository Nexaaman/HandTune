import cv2
import time
import mediapipe as mp

class handDetector:
    def __init__(self, mode = False, hands = 2,complex=1, detect_conf = 0.5, track_conf = 0.5):
        self.mode = mode
        self.hands = hands
        self.detect_conf = detect_conf
        self.track_conf = track_conf
        self.complex = complex
        self.mphands = mp.solutions.hands
        self.hands = self.mphands.Hands(self.mode, self.hands,self.complex, self.detect_conf, self.track_conf)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, frame, draw = True):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(frame)

        if self.results.multi_hand_landmarks:
            for handLes in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(frame, handLes, self.mphands.HAND_CONNECTIONS)
        return frame

    def findPositions(self, frame , handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h,w,c = frame.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id,cx,cy])
                if draw:
                    cv2.circle(frame,(cx,cy), 15, (255,0,255),cv2.FILLED)
        return lmList

def main():
    ptime = 0
    ctime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Error")
            break
        frame = detector.findHands(frame)
        lmList = detector.findPositions(frame,False)
        if len(lmList)!=0:
            print(lmList[4])
        ctime = time.time()
        fps = 1 / (ctime - ptime)
        ptime = ctime
        cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255.0, 255), 2)
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()