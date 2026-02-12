from fastapi import APIRouter, HTTPException, status, Depends
from app.database.mongo import get_db
from app.schemas.auth_schema import RegisterSchema, LoginSchema, TokenSchema, VerifyOtpSchema, UserDetailsSchema
from app.models.user import User
from app.utils.token import hash_password, verify_password, create_access_token, get_current_user
from app.services.email_service import send_otp_email
from app.utils.otp import generate_otp, is_otp_expired
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
async def register(user_data: RegisterSchema):
    db = get_db()
    
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        user = User.from_dict(existing_user)
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered and verified. Please login instead.",
            )
        
    existing_pending = await db.pending_registrations.find_one({"email": user_data.email})
    if existing_pending:
        if not is_otp_expired(existing_pending["created_at"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP already sent. Please check your email and verify within 10 minutes.",
            )
        otp = generate_otp()
        await db.pending_registrations.update_one(
            {"email": user_data.email},
            {"$set": {
                "password": hash_password(user_data.password),
                "full_name": user_data.full_name,
                "latitude": user_data.latitude,
                "longitude": user_data.longitude,
                "otp": otp,
                "created_at": datetime.now(timezone.utc)
            }}
        )
    else:
        otp = generate_otp()
        pending_data = {
            "email": user_data.email,
            "password": hash_password(user_data.password),
            "full_name": user_data.full_name,
            "latitude": user_data.latitude,
            "longitude": user_data.longitude,
            "otp": otp,
            "created_at": datetime.now(timezone.utc),
        }
        await db.pending_registrations.insert_one(pending_data)
    
    email_sent = await send_otp_email(user_data.email, otp)
    if not email_sent:
        await db.pending_registrations.delete_one({"email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again.",
        )
    
    return {
        "message": "Verification code sent to your email. Please verify to complete registration.",
        "email": user_data.email,
    }


@router.post("/verify-otp", response_model=dict)
async def verify_otp(otp_data: VerifyOtpSchema):
    db = get_db()
    
    pending = await db.pending_registrations.find_one({"email": otp_data.email})
    if not pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending registration found. Please register first.",
        )
    
    if is_otp_expired(pending["created_at"]):
        await db.pending_registrations.delete_one({"email": otp_data.email})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please register again.",
        )
    
    if pending["otp"] != otp_data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP. Please try again.",
        )
    
    user = User(
        email=pending["email"],
        full_name=pending["full_name"],
        hashed_password=pending["password"],
        latitude=pending["latitude"],
        longitude=pending["longitude"],
        is_verified=True,
    )
    
    result = await db.users.insert_one(user.to_dict())
    await db.pending_registrations.delete_one({"email": otp_data.email})
    
    return {
        "message": "Email verified successfully. Registration complete.",
        "user_id": str(result.inserted_id),
        "email": otp_data.email,
    }


@router.post("/login", response_model=TokenSchema)
async def login(credentials: LoginSchema):
    db = get_db()
    
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    user = User.from_dict(user_doc)
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email before logging in.",
        )
    
    access_token = create_access_token(user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 24 * 3600,
    }


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully. Please discard the token."}


@router.get("/me", response_model=UserDetailsSchema)
async def get_current_user_details(current_user: str = Depends(get_current_user)):
    db = get_db()
    
    user_doc = await db.users.find_one({"email": current_user})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user = User.from_dict(user_doc)
    
    return UserDetailsSchema(
        email=user.email,
        full_name=user.full_name,
        latitude=user.latitude,
        longitude=user.longitude,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )
