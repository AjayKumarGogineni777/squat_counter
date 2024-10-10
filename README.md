# Real-time Squat Analyzer

This project is a real-time squat analyzer built with React. It allows users to upload a video and analyze the number of squats performed in the video.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed [Node.js](https://nodejs.org/) (which includes npm).
- You have a running backend server at `http://localhost:8000`.

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the dependencies:
    ```sh
    npm install
    ```
## Example Video

You can find an example video for testing [here](https://drive.google.com/file/d/17UyKVEEnrf7iVc7mJYRt4f_eBRTLa3Pu/view?usp=sharing).


## Usage

1. Start the React application:
    ```sh
    npm start
    ```

2. Open your browser and navigate to `http://localhost:3000`.

3. Upload a video file and start the analysis.

## Backend Server

Ensure you have a backend server running at `http://localhost:8000` that handles video uploads and WebSocket connections for real-time analysis.

## Dependencies

The following dependencies are required and will be installed when you run `npm install`:

- `react`
- `react-dom`
- `axios`
- `lucide-react`

## License

This project is licensed under the MIT License.