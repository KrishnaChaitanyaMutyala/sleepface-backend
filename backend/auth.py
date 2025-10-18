import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        # Use service account key or default credentials
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
        else:
            # Use default credentials (for development)
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred)

# Initialize Firebase on module load
initialize_firebase()

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """
    Verify Firebase ID token and return user data
    """
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(credentials.credentials)
        
        # Return user data
        return {
            "uid": decoded_token["uid"],
            "email": decoded_token.get("email"),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current user from Firebase token
    """
    return await verify_token(credentials)

async def verify_guest_user(user_id: str) -> bool:
    """
    Verify if user_id is a valid guest user
    """
    # Guest users have IDs starting with "guest_"
    return user_id.startswith("guest_")

async def create_guest_user() -> str:
    """
    Create a new guest user and return guest ID
    """
    import uuid
    guest_id = f"guest_{uuid.uuid4().hex[:8]}"
    return guest_id
