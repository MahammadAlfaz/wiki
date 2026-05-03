


from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.models.user import User, UserRole


router=APIRouter(prefix="/auth",tags=['auth'])

class RegisterRequest(BaseModel):
    email:EmailStr
    name:str
    password:str
    role:UserRole=UserRole.engineer

class TokenResponse(BaseModel):
    access_token:str
    token_type:str="bearer"
    role:str
    name:str
     
@router.post("/register" ,status_code=status.HTTP_201_CREATED)
def register(req:RegisterRequest,db:Session=Depends(get_db)):
    existing=db.query(User).filter(
        User.email==req.email).first()
    if existing:
        raise HTTPException(status_code=400,detail="Email already registered")
    user=User(
        email=req.email,
        name=req.name,
        hashed_password=hash_password(req.password),
        role=req.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "message":"User registered successfully","id":user.id,"role":user.role
    }

@router.post("/login",response_model=TokenResponse)
def login(
    form_data:OAuth2PasswordRequestForm=Depends(),
    db:Session=Depends(get_db)
):
    user=db.query(User).filter(
        User.email==form_data.username,
        User.is_active == True
    ).first()

    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token=create_access_token({
        "sub":str(user.id),
        "role":user.role
    })
    return TokenResponse(
        access_token=token,
        role=user.role,
        name=user.name
    )