import cv2
import os
import platform
import pulsectl
import math
import Hand as hd
import time
import numpy as np

if platform.system() == "Windows":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
elif platform.system() == "Linux":
    import pulsectl

if platform.system() == "Windows":
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
elif platform.system() == "Linux":
    pulse = pulsectl.Pulse('volume-control')
    sink = pulse.sink_list()[0]

def set_volume(volume_percent):
    if platform.system() == "Windows":
        # Windows volume control
        volume_range = volume.GetVolumeRange()
        min_volume = volume_range[0]
        max_volume = volume_range[1]
        volume_level = volume_percent / 100 * (max_volume - min_volume) + min_volume
        volume.SetMasterVolumeLevel(volume_level, None)
    elif platform.system() == "Linux":
        # Linux volume control
        volume_percent = max(0, min(100, int(volume_percent)))  # Ensure volume is between 0 and 100
        volume = volume_percent / 100.0
        pulse.volume_set_all_chans(sink, volume)
    elif platform.system() == "Darwin":
        # macOS volume control using osascript
        volume_percent = max(0, min(100, int(volume_percent)))
        os.system(f"osascript -e 'set volume output volume {volume_percent}'")


prevT = 0
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error")
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(3))
height = int(cap.get(4))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output = cv2.VideoWriter('output.mp4', fourcc,fps, (width,height))
detector = hd.handDetector(detect_conf = 0.7)
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Error")
        break
    currT = time.time()
    fps = 1/(currT - prevT)
    prevT = currT
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.putText(frame, str(int(fps)), (40,70), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,255), 2)
    frame = detector.findHands(frame)
    lmList = detector.findPositions(frame,draw = False)
    if len(lmList) !=0:
        #print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2,y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x2 + x1)//2 , (y2 + y1)//2
        cv2.circle(frame, (x1,y1), 12, (255,0,255),cv2.FILLED)
        cv2.circle(frame, (x2, y2), 12, (255, 0, 255), cv2.FILLED)
        #cv2.circle(frame, (cx,cy), 12, (255,0,255),cv2.FILLED)
        cv2.line(frame, (x1,y1) , (x2,y2), (255,0,255), 3)
        length = math.hypot(x2-x1, y2-y1)
        print(length)

        if length > 200:
            set_volume(100)
        elif length < 30:
            set_volume(0)
        else:
            volume_percent = np.interp(length, [30, 200], [0, 100])
            set_volume(volume_percent)

        if length < 30:
            cv2.circle(frame, (cx, cy), 12, (0, 255, 255), cv2.FILLED)
    output.write(frame)
cap.release()
output.release()
cv2.destroyAllWindows()
