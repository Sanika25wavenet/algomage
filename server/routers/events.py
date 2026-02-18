from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.event import EventCreate, EventResponse, EventInDB
from models.user import UserResponse
from auth.dependencies import get_current_photographer
from services.event_service import create_event, get_event_by_id, get_events_by_photographer
from config.settings import settings

router = APIRouter(prefix="/event", tags=["Events"])

# Photographer Endpoints

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_new_event(
    event: EventCreate,
    current_user: UserResponse = Depends(get_current_photographer)
):
    """
    Create a new event. Only for photographers.
    """
    try:
        user_id = str(current_user["_id"])
        new_event = await create_event(event, user_id)
        
        from services.event_service import generate_share_link
        share_link = await generate_share_link(new_event, user_id)
        
        return EventResponse(
            **new_event.dict(exclude={"id"}),
            id=str(new_event.id),
            share_link=share_link
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.get("/", response_model=List[EventResponse])
async def list_events(
    current_user: UserResponse = Depends(get_current_photographer)
):
    """
    List all events created by the current photographer.
    """
    user_id = str(current_user["_id"])
    events = await get_events_by_photographer(user_id)
    
    from services.event_service import generate_share_link
    resp = []
    for event in events:
        link = await generate_share_link(event, user_id)
        resp.append(EventResponse(**event.dict(exclude={"id"}), id=str(event.id), share_link=link))
    return resp


@router.get("/{photographer_slug}/{event_hex_id}/share-link", response_model=dict)
async def get_share_link_v2(
    photographer_slug: str,
    event_hex_id: str,
    current_user: UserResponse = Depends(get_current_photographer)
):
    """
    Get the shareable link for an event. Only for the event creator.
    """
    event = await get_event_by_id(event_hex_id, photographer_slug)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if the current user is the creator of the event
    if event.created_by != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to access this event")
        
    from services.event_service import generate_share_link
    return {"share_link": await generate_share_link(event, str(current_user["_id"]))}


# Public Endpoints

@router.get("/{photographer_slug}/{event_hex_id}", response_model=EventResponse)
async def get_event_details_v2(photographer_slug: str, event_hex_id: str):
    """
    Get event details by photographer slug and event hex ID. Public access for guests.
    """
    event = await get_event_by_id(event_hex_id, photographer_slug)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if not event.is_active:
        raise HTTPException(status_code=400, detail="Event is not active")
        
    from services.event_service import generate_share_link
    share_link = await generate_share_link(event, event.created_by)
    return EventResponse(**event.dict(exclude={"id"}), id=str(event.id), share_link=share_link)
