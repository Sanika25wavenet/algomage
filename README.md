# Intelligent Event Photo Retrieval System

## 🚀 Project Overview
An AI-powered system that allows users to find themselves in thousands of event photos by uploading a single selfie.
**Core Tech:** Python (FastAPI), FaceNet (PyTorch), MTCNN, FAISS, MongoDB, Next.js.

---

## 🛠️ Status (Phase 2)
- [x] **Project Setup**: Python/Node environment, MongoDB connection.
- [x] **Task 1: Image Preprocessing**: Production-grade loader.
- [x] **Task 2 & 3: Face Detection**: MTCNN implementation with validation & visualization.
- [x] **Task 4: Face Encoding**: Converting faces to vectors.
- [x] **Task 5: Indexing**: FAISS Search implementation.

---

## 📂 Modules & Features

### 1. Image Loader (`server/ml/image_loader.py`)
Acts as the secure gateway for all image inputs.
- **Auto-Orientation**: Fixes rotated phone photos using EXIF data.
- **Format Standardization**: Converts everything to RGB (fixes PNG/Alpha issues).
- **Optimization**: Resizes large images (>1600px) for faster AI processing.
- **Validation**:
    - Rejects files > 15MB.
    - Rejects tiny images < 100px.
    - Captures corrupted files safely.
    - Supports batch processing.

### 2. Face Detector (`server/ml/face_detector.py`)
Finds faces in group photos using **MTCNN**.
- **Multi-Face Detection**: Tuned to find all faces in a crowd.
- **Safety**: Clamps bounding boxes to image dimensions to prevent crashes.
- **Filtering**: Ignores small background faces (<20px).
- **Visualization**: Can draw red bounding boxes on images for debugging.

### 3. Face Quality Checker (`server/ml/quality_checker.py`)
Ensures only high-quality faces are processed.
- **Blur Check**: Rejects fuzzy images (Laplacian Variance < 100).
- **Darkness Check**: Rejects shadowed faces (Brightness < 40).
- **Reasoning**: Returns specific reasons for rejection (e.g., "Too Blurry").

### 4. Face Encoder (`server/ml/face_encoder.py`)
Converts faces into 512-dimensional vectors (embeddings).
- **Model**: InceptionResnetV1 (FaceNet).
- **Batch Processing**: Processes multiple faces at once for speed.
- **Output**: L2-Normalized vectors ready for comparison.

---

## 🧪 How to Run Tests

### Standard Face Detection Test
Run this to see if the AI finds faces in your sample images:
```bash
cd server
uv run python -m test_detection
```
*Check `server/debug_output/` to see the images with red boxes drawn around faces.*

### Face Quality Test
Run this to verify blur/darkness rejection:
```bash
cd server
uv run python -m test_quality
```
*Creates synthetic test images in `server/test_quality_output/`.*

### Face Encoding Test
Run this to verify that faces are converted to vectors:
```bash
cd server
uv run python -m test_encoding
```
*Should output `Shape: (N, 512)` and `Magnitude: 1.0000`.*

### Validation & Stress Test
Run this to verify the system correctly rejects bad files (corrupt, too small, etc):
```bash
cd server
uv run python -m test_validation
```

---

## 🚀 How to Run (One Command)

You can now start the entire stack (Redis, Backend, Celery, and Frontend) with a single command.

### Option A: Using NPM (Recommended - Unified Terminal)
Run this from the root directory:
```bash
npm run dev
```
*Requires Node.js. Uses `concurrently` to show all logs in one window.*

### Option B: Using PowerShell (Windows Native)
Run this from the root directory:
```powershell
.\dev.ps1
```
*Launches Redis in Docker and opens three separate terminal windows for the API, Worker, and Frontend.*

### Stop Services
To stop the infrastructure (Redis):
```bash
npm run stop
# OR
docker-compose down
```

---

## 📂 Data Organization

The system uses a name-based slug system for organizing uploads and URLs.

### 📁 Directory Structure
```text
server/uploads/
├── photographer-name-slug/
│   ├── event-name-slug/
│   │   ├── photo1.jpg
│   │   └── photo2.jpg
```

### 🔗 URL Structure
- **Photographer Dashboard**: `http://localhost:3000/dashboard`
- **Guest Gallery**: `http://localhost:3000/event/{photographer-slug}/{event-slug}`

---

## 📝 Setup Instructions
...
