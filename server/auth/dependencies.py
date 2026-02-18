from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
import jwt
from config.settings import settings
from config.database import db
from models.user import UserRole
from auth.utils import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        # token_data = {"sub": user_id, "role": role}
    except PyJWTError:
        raise credentials_exception
    
    # Database lookup
    user = await db.db.users.find_one({"_id": user_id}) 
    
    if user is None:
        from bson import ObjectId
        try:
             user = await db.db.users.find_one({"_id": ObjectId(user_id)})
        except:
             pass
        
        if user is None:
            raise credentials_exception
            
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    return current_user

async def get_current_admin(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_photographer(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("role") not in [UserRole.PHOTOGRAPHER, UserRole.ADMIN]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
