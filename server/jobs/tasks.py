from config.celery_app import celery_app
from config.database import db
from ml.face_detector import face_detector
from ml.face_encoder import face_encoder
from ml.image_loader import image_loader
from services.faiss_service import faiss_service
import logging
import asyncio
from typing import List, Dict
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Helper to run async db operations in sync celery task
def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Should not happen in standard Celery worker, but safety net
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)

@celery_app.task(name="test_celery_task")
def test_celery_task(word: str):
    """
    Simple test task to verify Celery is working.
    Simulates a 5-second delay.
    """
    logger.info(f"Received task with word: {word}")
    time.sleep(5)
    logger.info(f"Task completed: {word}")
    return f"Processed {word}"

@celery_app.task(name="process_batch_upload", bind=True, max_retries=3)
def process_batch_upload(self, file_paths: List[str], event_id: str, uploader_id: str, photographer_name: str = None):
    """
    Celery wrapper for batch processing.
    """
    task_id = self.request.id
    return process_batch_upload_logic(task_id, file_paths, event_id, uploader_id, photographer_name)

def process_batch_upload_logic(task_id: str, file_paths: List[str], event_id: str, uploader_id: str, photographer_name: str = None):
    """
    Core logic for batch processing. Can be called by Celery or BackgroundTasks.
    """
    logger.info(f"[{task_id}] Processing batch of {len(file_paths)} images for event {event_id} by {photographer_name or uploader_id}")

    all_detections = []
    processed_count = 0
    failed_count = 0

    try:
        # 1. Detect Faces in all images
        for idx, file_path in enumerate(file_paths):
            try:
                # Load Image
                image = image_loader.load_from_path(file_path)
                if image is None:
                    logger.warning(f"[{task_id}] Failed to load image: {file_path}")
                    failed_count += 1
                    continue

                # Detect Faces
                detections = face_detector.detect_faces(image)
                processed_count += 1
                
                # Progress logging
                if processed_count % 10 == 0:
                    logger.info(f"[{task_id}] Processed {processed_count}/{len(file_paths)} images...")
                
                if not detections:
                    continue

                # Add metadata to detections
                for det in detections:
                    det['event_id'] = event_id
                    det['photographer_name'] = photographer_name
                    det['file_path'] = file_path
                    det['batch_task_id'] = task_id
                
                all_detections.extend(detections)

            except Exception as e:
                logger.error(f"[{task_id}] Error processing file {file_path}: {e}")
                failed_count += 1

        logger.info(f"[{task_id}] Detection complete. Found {len(all_detections)} faces in {processed_count} images.")

        if not all_detections:
            return {
                "status": "completed", 
                "images_processed": processed_count, 
                "faces_found": 0,
                "failed": failed_count
            }

        # 2. Encode Faces (Batch)
        # face_encoder handles batching internally if list is large
        embeddings_dicts = face_encoder.encode_faces(all_detections)
        
        # 3. Prepare for FAISS & DB
        vectors = []
        face_records = []
        
        for i, res in enumerate(embeddings_dicts):
            if 'embedding' not in res or res['embedding'] is None:
                continue
                
            embedding_list = res['embedding'].tolist()
            vectors.append(embedding_list)
            
            # Record for MongoDB - Refined Schema
            face_records.append({
                "event_id": res.get('event_id'),
                "photographer_name": res.get('photographer_name'),
                "file_path": res.get('file_path'),
                "task_id": task_id,
                "bounding_box": res['box'],
                "confidence": res['confidence'],
                "image_embedded_number": -1, # To be updated
                "created_at": datetime.now() 
            })

        if vectors:
            # 4. Add to FAISS (Thread-Safe / Process-Safe)
            # In a simple BackgroundTasks scenario without Redis, locking might be skipped or mocked if Redis unavailable
            # But let's try to be robust. 
            try:
                from redis import Redis
                from config.settings import settings
                
                # Connect to Redis for locking
                redis_client = Redis.from_url(settings.REDIS_URL)
                # Simple check if redis is reachable
                redis_client.ping()
                
                lock = redis_client.lock("faiss_index_update_lock", timeout=30)
                acquired = lock.acquire(blocking=True, timeout=5) # Add timeout to avoid hanging
                
                if not acquired:
                     logger.warning(f"[{task_id}] Could not acquire FAISS lock (Redis). Proceeding without lock (Risk of race condition if multiple workers).")
            except Exception as e:
                logger.warning(f"[{task_id}] Redis lock failed (likely no Redis), proceeding without lock: {e}")
                acquired = False

            try:
                # Sync with disk before adding
                faiss_service.reload_index()
                
                # Add and Save
                ids = faiss_service.add_vectors(vectors)
                faiss_service.save_index()
            finally:
                if acquired:
                    try:
                         lock.release()
                    except:
                        pass
            
            # Update IDs in records
            for i, faiss_id in enumerate(ids):
                face_records[i]['image_embedded_number'] = int(faiss_id)

            # 5. Save to MongoDB in Chunks
            from pymongo import MongoClient
            from config.settings import settings 
            
            client = MongoClient(settings.MONGODB_URL)
            database = client[settings.DATABASE_NAME]
            
            if face_records:
                # Chunked insertion to avoid huge BSON documents and show progress in DB
                chunk_size = 100
                total_inserted = 0
                for i in range(0, len(face_records), chunk_size):
                    chunk = face_records[i:i + chunk_size]
                    database.faces.insert_many(chunk)
                    total_inserted += len(chunk)
                    logger.info(f"[{task_id}] Progress: Saved {total_inserted}/{len(face_records)} face records to DB")
                
            client.close()

        return {
            "status": "completed",
            "images_processed": processed_count,
            "failed_images": failed_count,
            "faces_indexed": len(vectors),
            "records_stored": len(face_records)
        }

    except Exception as e:
        logger.error(f"[{task_id}] Batch task failed: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}
