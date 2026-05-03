from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.security import decode_token
from app.db.database import get_db
from sqlalchemy.orm import Session

from app.models.user import User, UserRole

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user( token:str=Depends(oauth2_scheme), db:Session=Depends(get_db))->User:
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        payload=decode_token(token)
        user_id:str=payload.get('sub')
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user=db.query(User).filter(
        User.id==int(user_id),
        User.is_active==True,
    ).first()

    if not user:
        raise credentials_exception
    return user


def require_admin(current_user:User=Depends(get_current_user))->User:
    """
    Use this dependency on any route that require admin access
    Raises 403 if the current user is not an admin
    """

    if current_user.role!=UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user