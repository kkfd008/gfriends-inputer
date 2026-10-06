# Lib Directory Instructions

## Scope
This directory contains computer vision logic and pre-trained AI models used for face detection and avatar cropping.

## Key Components
- `cv2dnn.py`: Implementation of OpenCV DNN (Deep Neural Network) for local face detection.
- `opencv_face_detector_uint8.pb`: Pre-trained TensorFlow model.
- `opencv_face_detector.pbtxt`: Model configuration.

## Conventions
- **Graceful Degradation:** AI logic must handle missing model files or incompatible environments (e.g., CPU/OS issues) without crashing the main program.
- **Image Handling:** 
  - Functions should accept `PIL.Image` objects or binary data.
  - Coordinate systems must be scaled relative to original image dimensions.
- **Model Loading:** Check for file existence before attempting to initialize `cv2.dnn.readNet`.
