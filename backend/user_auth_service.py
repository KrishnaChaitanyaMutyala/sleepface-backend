"""
User Authentication Service
Handles user registration, login, and authentication using JWT tokens
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import UserRegistration, UserLogin, UserProfile, AuthResponse, PasswordResetRequest, PasswordReset, UserUpdate
import os

# Simple password hashing using hashlib (for development)
def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    return f"{salt}:{hashlib.sha256((password + salt).encode()).hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, hash_value = hashed_password.split(':')
        return hashlib.sha256((plain_password + salt).encode()).hexdigest() == hash_value
    except:
        return False

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class UserAuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users_collection = db.users
        self.sessions_collection = db.user_sessions

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return verify_password(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return hash_password(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    async def register_user(self, user_data: UserRegistration) -> AuthResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.users_collection.find_one({"email": user_data.email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Generate user ID
            user_id = f"user_{secrets.token_hex(8)}"
            
            # Hash password
            hashed_password = self.get_password_hash(user_data.password)
            
            # Create user document
            user_doc = {
                "user_id": user_id,
                "email": user_data.email,
                "display_name": user_data.display_name,
                "password_hash": hashed_password,
                "is_premium": False,
                "streak_count": 0,
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "profile_picture_url": None,
                "is_active": True
            }
            
            # Insert user into database
            result = await self.users_collection.insert_one(user_doc)
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )

            # Create tokens
            access_token = self.create_access_token({"user_id": user_id, "email": user_data.email})
            refresh_token = self.create_refresh_token({"user_id": user_id})

            # Store refresh token
            await self.sessions_collection.insert_one({
                "user_id": user_id,
                "refresh_token": refresh_token,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            })

            # Create user profile
            user_profile = UserProfile(
                user_id=user_id,
                email=user_data.email,
                display_name=user_data.display_name,
                is_premium=False,
                streak_count=0,
                created_at=user_doc["created_at"],
                last_active=user_doc["last_active"],
                profile_picture_url=None
            )

            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_profile
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error registering user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )

    async def login_user(self, login_data: UserLogin) -> AuthResponse:
        """Authenticate user and return tokens"""
        try:
            # Find user by email
            user = await self.users_collection.find_one({"email": login_data.email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            # Check if user is active
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )

            # Verify password
            if not self.verify_password(login_data.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            # Update last active
            await self.users_collection.update_one(
                {"user_id": user["user_id"]},
                {"$set": {"last_active": datetime.utcnow()}}
            )

            # Create tokens
            access_token = self.create_access_token({"user_id": user["user_id"], "email": user["email"]})
            refresh_token = self.create_refresh_token({"user_id": user["user_id"]})

            # Store refresh token
            await self.sessions_collection.insert_one({
                "user_id": user["user_id"],
                "refresh_token": refresh_token,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            })

            # Create user profile
            user_profile = UserProfile(
                user_id=user["user_id"],
                email=user["email"],
                display_name=user["display_name"],
                is_premium=user.get("is_premium", False),
                streak_count=user.get("streak_count", 0),
                created_at=user["created_at"],
                last_active=datetime.utcnow(),
                profile_picture_url=user.get("profile_picture_url")
            )

            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_profile
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error logging in user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to authenticate user"
            )

    async def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                return None

            return UserProfile(
                user_id=user["user_id"],
                email=user["email"],
                display_name=user["display_name"],
                is_premium=user.get("is_premium", False),
                streak_count=user.get("streak_count", 0),
                created_at=user["created_at"],
                last_active=user["last_active"],
                profile_picture_url=user.get("profile_picture_url")
            )
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    async def update_user_profile(self, user_id: str, update_data: UserUpdate) -> UserProfile:
        """Update user profile"""
        try:
            update_fields = {}
            if update_data.display_name is not None:
                update_fields["display_name"] = update_data.display_name
            if update_data.profile_picture_url is not None:
                update_fields["profile_picture_url"] = update_data.profile_picture_url

            if not update_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update"
                )

            update_fields["last_active"] = datetime.utcnow()

            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Return updated user profile
            return await self.get_user_by_id(user_id)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error updating user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )

    async def logout_user(self, user_id: str, refresh_token: str) -> bool:
        """Logout user by invalidating refresh token"""
        try:
            result = await self.sessions_collection.delete_one({
                "user_id": user_id,
                "refresh_token": refresh_token
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error logging out user: {e}")
            return False

    async def refresh_access_token(self, refresh_token: str) -> AuthResponse:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

            # Check if refresh token exists in database
            session = await self.sessions_collection.find_one({
                "user_id": user_id,
                "refresh_token": refresh_token
            })

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            # Get user data
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            # Create new access token
            access_token = self.create_access_token({"user_id": user_id, "email": user["email"]})

            # Update last active
            await self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"last_active": datetime.utcnow()}}
            )

            # Create user profile
            user_profile = UserProfile(
                user_id=user["user_id"],
                email=user["email"],
                display_name=user["display_name"],
                is_premium=user.get("is_premium", False),
                streak_count=user.get("streak_count", 0),
                created_at=user["created_at"],
                last_active=datetime.utcnow(),
                profile_picture_url=user.get("profile_picture_url")
            )

            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_profile
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error refreshing token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to refresh token"
            )
