from typing import Annotated, Optional
from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from bson import ObjectId

PyObjectId = Annotated[str, BeforeValidator(str)]

class EventBase(BaseModel):
    name: str
    is_active: bool = True

class EventCreate(EventBase):
    pass

class EventInDB(EventBase):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    event_id: str  # Now a string slug (e.g., 'summer-wedding-2024')
    created_by: str  # User ID of the photographer
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class EventResponse(EventBase):
    id: str
    event_id: str
    created_at: datetime
    share_link: Optional[str] = None
