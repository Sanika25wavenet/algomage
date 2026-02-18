# Intelligent Event Photo Retrieval System 📸

An AI-powered system that allows users to upload a selfie and instantly retrieve all photos of themselves from large event albums. Built with privacy, speed, and scalability in mind.

## 🚀 Project Status
**Current Phase:** Phase 2 (Infrastructure & Security) - **Completed**

## 🏗️ Architecture

*   **Backend API:** FastAPI (High-performance, async Python framework)
*   **Database:** MongoDB (via Motor) - Stores user profiles and image metadata.
*   **Vector Search:** FAISS (Facebook AI Similarity Search) - Ultra-fast face embedding search.
*   **ML Pipeline:** PyTorch + FaceNet (Inception Resnet V1) - Generates 512-dim face embeddings.
*   **Background Tasks:** Celery + Redis - Handles heavy image processing asynchronously.
*   **Authentication:** JWT (JSON Web Tokens) with **bcrypt** password hashing.

---

## 📅 Progress Overview

### Phase 1: Core ML Engine 🧠
Focused on the ability to detect and recognize faces accurately.
*   **Face Detection:** Implemented **MTCNN** to detect faces in varying lighting and angles.
*   **Feature Extraction:** Integrated **Inception Resnet V1** (pretrained on VGGFace2/Casia-WebFace) to output high-quality 512-dimensional embeddings.
*   **Optimization:** Added batch processing and CPU compatibility to ensure the system runs smoothly without expensive GPUs.
*   **Quality Control:** Added logic to reject blurry or low-quality face detections.

### Phase 2: Infrastructure, Security & Scalability 🛡️
Focused on turning the ML script into a robust, multi-user web application.
*   **Secure Authentication:**
    *   Implemented User Registration & Login endpoints.
    *   Secured passwords using **bcrypt** hashing.
    *   Added **Role-Based Access Control (RBAC)**: Admins, Photographers, Guests.
*   **Vector Database Integration:**
    *   Set up **FAISS** with `IndexFlatL2` for 100% accurate exact search on face embeddings.
    *   Implemented persistence to save/load the index from disk.
*   **Asynchronous Processing:**
    *   Configured **Redis** as a message broker.
    *   Set up **Celery** workers to handle image uploads in the background, preventing API timeouts during heavy processing.
    *   Created `process_image_upload` task to handle the entire pipeline (Load -> Detect -> Encode -> Index -> Save).

### Phase 3: Event Management & Sharing 🔗
Focused on usability and sharing capabilities.
*   **Numeric Event IDs:** Implemented auto-incrementing, human-readable event IDs (e.g., `event/8`, `event/9`).
*   **Shareable Links:** Photographers can generate unique, shareable links for their events.
*   **Public Access:** Guests can access event details via share links without requiring a login (for public events).

---

## 🛠️ Setup & Installation

### Prerequisites
*   Python 3.10+
*   Redis Server (Running locally or via Docker)
*   MongoDB Atlas URI (or local MongoDB)

### 1. clone & Install Dependencies
```bash
git clone <repo-url>
cd server
python -m venv .venv
.\.venv\Scripts\activate
pip install .   # Installs dependencies from pyproject.toml
```

### 2. Environment Variables
Create a `.env` file in the `server/` directory:
```ini
MONGODB_URL=mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=event_photo_retrieval
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_super_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
BASE_URL=http://localhost:8000
```

### 3. Run the Services

**Start the API Server:**
```powershell
.\.venv\Scripts\python -m uvicorn main:app --reload
```
*Access API Docs at: http://localhost:8000/docs*

**Start the Celery Worker (Background Tasks):**
```powershell
# Windows
.\.venv\Scripts\python -m celery -A config.celery_app worker --loglevel=info --pool=solo

# Linux/Mac
./.venv/bin/celery -A config.celery_app worker --loglevel=info
```

**Start the Frontend Client:**
```powershell
cd client
npm install
npm run dev
```
*Access Frontend at: http://localhost:3000*

## 🧪 Testing

Run these scripts to verify different components:

*   `.\.venv\Scripts\python test_auth.py`: Verifies Login/Register flow.
*   `.\.venv\Scripts\python test_celery.py`: Verifies Redis connection.
*   `.\.venv\Scripts\python test_faiss.py`: Verifies Vector Index operations.
*   `.\.venv\Scripts\python test_encoding.py`: Verifies FaceNet model output.
*   `.\.venv\Scripts\python test_event_flow.py`: Verifies Event Creation, Sharing, and Public Access.

---

## 🔮 Next Steps (Phase 4)
*   Frontend Integration (Next.js).
*   Real-world stress testing.
*   Advanced query filters.
