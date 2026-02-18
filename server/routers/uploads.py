from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
from typing import List
import logging

logger = logging.getLogger(__name__)

from auth.dependencies import get_current_photographer
from models.user import UserResponse
from celery.result import AsyncResult

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def upload_images(
    event_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: UserResponse = Depends(get_current_photographer)
):
    """
    Upload multiple images for processing.
    - Saves files to disk under uploads/{event_id}/
    - Triggers background task for batch processing.
    - Returns Task ID.
    """
    # Create photographer-specific and event-specific directory
    from services.event_service import slugify
    photographer_slug = slugify(current_user["name"])
    event_dir = os.path.join(UPLOAD_DIR, photographer_slug, event_id)
    os.makedirs(event_dir, exist_ok=True)
    
    saved_file_paths = []

    try:
        for file in files:
            if not file.content_type.startswith("image/"):
                continue 
            
            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(event_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            saved_file_paths.append(os.path.abspath(file_path))
            
        if not saved_file_paths:
             raise HTTPException(400, "No valid images uploaded")

        # Trigger Processing
        # Default to Celery for scalability, fallback to local BackgroundTasks if Redis is down (Dev mode)
        from jobs.tasks import process_batch_upload, process_batch_upload_logic
        from redis import Redis
        from config.settings import settings
        
        task_id = str(uuid.uuid4())
        use_celery = False

        # Quick check if Redis is available to avoid Celery's long retry loop
        try:
            r = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
            if r.ping():
                use_celery = True
                r.close()
        except Exception:
            use_celery = False

        if use_celery:
            try:
                # Try to start Celery task
                celery_task = process_batch_upload.delay(saved_file_paths, event_id, str(current_user["_id"]), current_user["name"])
                task_id = celery_task.id
                message = f"Batch processing started (Celery Task: {task_id})"
            except Exception as e:
                # In case it fails despite ping
                logger.warning(f"Celery task failed to start despite Redis ping. Falling back. Error: {e}")
                background_tasks.add_task(process_batch_upload_logic, task_id, saved_file_paths, event_id, str(current_user["_id"]), current_user["name"])
                message = f"Batch processing started (Background Task: {task_id})"
        else:
            logger.info("Redis not reachable. Using BackgroundTasks fallback.")
            background_tasks.add_task(process_batch_upload_logic, task_id, saved_file_paths, event_id, str(current_user["_id"]), current_user["name"])
            message = f"Batch processing started (Background Task: {task_id})"
        
        from services.event_service import get_event_by_id, generate_share_link
        event_doc = await get_event_by_id(event_id)
        share_link = await generate_share_link(event_doc, str(current_user["_id"])) if event_doc else f"http://localhost:3000/event/{photographer_slug}/{event_id}"

        return {
            "message": message,
            "task_id": task_id,
            "files_saved": len(saved_file_paths),
            "share_link": share_link
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(500, detail=f"Failed to upload images: {str(e)}")

@router.get("/status/{task_id}")
async def get_task_status(task_id: str, current_user: UserResponse = Depends(get_current_photographer)):
    """
    Check the status of a background processing task.
    """
    task_result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    
    if task_result.failed():
        response["error"] = str(task_result.result)
        
    return response
