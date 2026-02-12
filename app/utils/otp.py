import random
import string
from datetime import datetime, timedelta, timezone


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def is_otp_expired(created_at: datetime, expiry_minutes: int = 10) -> bool:
    """Check if OTP has expired"""
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    return now > created_at + timedelta(minutes=expiry_minutes)