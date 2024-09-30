# Real-time Squat Analyzer Backend

This project is the backend for a real-time squat analyzer. It processes video uploads and uses MediaPipe for pose detection to count squats.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed [Python 3.8+](https://www.python.org/downloads/).
- You have installed [pip](https://pip.pypa.io/en/stable/installation/).

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```

3. Activate the virtual environment:

    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Start the backend server:
    ```sh
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

2. Ensure the frontend is running on port 3000.

3. The backend server will handle video uploads and WebSocket connections for real-time analysis.

## API Endpoints

- **POST /upload/**: Upload a video file.
- **WebSocket /ws**: WebSocket endpoint for real-time squat analysis.

## Dependencies

The following dependencies are required and will be installed when you run `pip install -r requirements.txt`:

- fastapi
- uvicorn
- opencv-python
- mediapipe
- numpy

## License

This project is licensed under the MIT License.