from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from config.database import db
from models.user import UserCreate, UserInDB, Token, UserResponse, UserRole
from auth.utils import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    try:
        # Check if user exists
        existing_user = await db.db.users.find_one({"email": user.email})
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user dict
        user_data = user.model_dump(exclude={"password"})
        user_in_db = UserInDB(
            **user_data,
            hashed_password=hashed_password
        )
        
        # Insert
        new_user = await db.db.users.insert_one(user_in_db.model_dump(by_alias=True, exclude={"id"}))
        
        # Return created user
        return UserResponse(
            id=str(new_user.inserted_id),
            created_at=user_in_db.created_at,
            **user.model_dump(exclude={"password"})
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Find user
    user = await db.db.users.find_one({"email": form_data.username}) # OAuth2 form uses 'username' for email
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    # Create token
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user.get("role", "guest")}
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.get("role", "guest")}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[UserInDB, Depends(get_current_active_user)]):
    # Convert _id to id for response
    user_dict = current_user
    user_dict["id"] = str(user_dict["_id"])
    return user_dict
