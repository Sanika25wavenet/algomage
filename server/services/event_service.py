from models.event import EventCreate, EventInDB
from config.database import db
from config.settings import settings
import logging
from pymongo import ReturnDocument

logger = logging.getLogger(__name__)

import re
from unicodedata import normalize

def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    """
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

async def create_event(event_create: EventCreate, user_id: str) -> EventInDB:
    """
    Create a new event with a slug-based event_id.
    """
    try:
        # Generate slug from event name
        base_slug = slugify(event_create.name)
        
        # No longer need a slug loop, we'll use the MongoDB generated ID for uniqueness
        event_id = slugify(event_create.name)

        from datetime import datetime
        event_data = event_create.dict()
        event_in_db = EventInDB(
            **event_data,
            event_id=event_id,
            created_by=str(user_id),
            created_at=datetime.utcnow()
        )
        
        # Save to database
        event_dict = event_in_db.dict(by_alias=True, exclude={"id"})
        result = await db.db.events.insert_one(event_dict)
        
        # Add the generated _id back to the model
        event_in_db.id = str(result.inserted_id)
        
        return event_in_db
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise e

async def get_event_by_id(event_hex_id: str, photographer_slug: str = None):
    """
    Retrieve an event by its hex _id. 
    The photographer_slug is optional and used for URL validation or context.
    """
    try:
        from bson import ObjectId
        if not ObjectId.is_valid(event_hex_id):
            return None
            
        event = await db.db.events.find_one({"_id": ObjectId(event_hex_id)})
        
        if event:
            return EventInDB(**event)
        return None
    except Exception as e:
        logger.error(f"Error retrieving event by ID {event_hex_id}: {e}")
        return None

async def generate_share_link(event_doc: EventInDB, user_id: str) -> str:
    """
    Generate a shareable link using photographer name slug and event hex ID.
    Format: /event/{photographer_slug}/{event_hex_id}
    """
    from bson import ObjectId
    user = await db.db.users.find_one({"_id": ObjectId(user_id)})
    photographer_slug = slugify(user["name"]) if user else "photographer"
    
    # We use the document's MongoDB ID as the unique event identifier
    return f"{settings.BASE_URL}/event/{photographer_slug}/{str(event_doc.id)}"

async def get_events_by_photographer(user_id: str):
    """
    Retrieve all events created by a specific photographer.
    """
    try:
        cursor = db.db.events.find({"created_by": user_id}).sort("created_at", -1)
        events_list = await cursor.to_list(length=100)
        return [EventInDB(**event) for event in events_list]
    except Exception as e:
        logger.error(f"Error retrieving events for user {user_id}: {e}")
        return []
