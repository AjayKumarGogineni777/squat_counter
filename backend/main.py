import cv2
import mediapipe as mp
import numpy as np
from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_dir = 'videos/uploads'
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

async def process_frame(frame, pose, prev_hip_angle, squat_in_progress):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    
    squat_detected = False
    hip_angle = None
    
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
        
        hip_angle = calculate_angle(hip, knee, ankle)

        # Get landmarks
        shoulder_left = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        shoulder_right = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip_left = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        hip_right = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        knee_left = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        knee_right = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
        
        # hip_angle_new = calculate_angle(hip_left, knee_left, hip_right)

        # Check if the frame is in a front view
        shoulder_distance = np.linalg.norm(np.array([shoulder_left.x, shoulder_left.y]) - np.array([shoulder_right.x, shoulder_right.y]))
        hip_distance = np.linalg.norm(np.array([hip_left.x, hip_left.y]) - np.array([hip_right.x, hip_right.y]))
        knee_distance = np.linalg.norm(np.array([knee_left.x, knee_left.y]) - np.array([knee_right.x, knee_right.y]))

        # Determine front view if shoulders and hips are approximately aligned and knees are directly under hips
        if abs(shoulder_distance - hip_distance) < 0.1 and abs(shoulder_left.x - shoulder_right.x) < 0.1 and abs(knee_left.x - knee_right.x) < 0.1:
            front_view_detected = True
        else:
            front_view_detected = False

        # Check for the bottom of the squat (hip angle < 100°) and standing (hip angle > 160°)
        if prev_hip_angle is not None:
            if (prev_hip_angle < 130 and prev_hip_angle > 100 and hip_angle < 125) or (prev_hip_angle < 140 and prev_hip_angle > 100 and hip_angle < 140 and front_view_detected):
                # print(f'Previous hip_angle: {prev_hip_angle}, hip_angle: {hip_angle}')
                squat_in_progress = True  # Squat is in progress (person is in a deep squat)
            # if hip_angle > 160:
            #     print(f'Standing up: hip_angle: {hip_angle}')
            if hip_angle > 160 and squat_in_progress:
                print(f'Standing up: hip_angle: {hip_angle}')
                squat_detected = True  # Increment squat count only when the person stands up
                squat_in_progress = False  # Reset for the next squat
            else:
                squat_detected = False
    # print(f'hip_angle: {hip_angle}, squat_detected: {squat_detected}, squat_in_progress: {squat_in_progress}')
    return frame, squat_detected, hip_angle, squat_in_progress

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        return JSONResponse(content={"filename": unique_filename})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        filename = await websocket.receive_text()
        file_path = os.path.join(uploads_dir, filename)
        
        if not os.path.exists(file_path):
            await websocket.send_json({"error": "File not found"})
            return
        
        video_capture = cv2.VideoCapture(file_path)
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        
        # Adjust frame skip for faster processing
        frame_skip = max(1, int(fps // 15))  # Process roughly 15 frames per second

        total_squats = 0
        prev_hip_angle = None
        squat_in_progress = False  # Initially no squat in progress
        frame_count = 0

        while True:
            success, frame = video_capture.read()
            if not success:
                break
            
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            processed_frame, squat_detected, hip_angle, squat_in_progress = await process_frame(frame, pose, prev_hip_angle, squat_in_progress)
            
            if squat_detected:
                total_squats += 1  # Increment squat count only when squat_detected is True
            
            prev_hip_angle = hip_angle  # Track the hip angle for the next frame
            
            _, buffer = cv2.imencode('.jpg', processed_frame)
            await websocket.send_bytes(buffer.tobytes())
            await websocket.send_json({
                "total_squats": total_squats
            })
            
            # No need for asyncio.sleep with frame skipping
    
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        if 'video_capture' in locals():
            video_capture.release()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)