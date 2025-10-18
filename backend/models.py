from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class AnalysisError(Exception):
    """Base exception for analysis errors"""
    def __init__(self, message: str, error_code: str = "ANALYSIS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class NoFaceDetectedError(AnalysisError):
    """Raised when no face is detected in the uploaded image"""
    def __init__(self, message: str = "No face detected in the uploaded image. Please upload a clear selfie with your face visible."):
        super().__init__(message, "NO_FACE_DETECTED")

class ImageProcessingError(AnalysisError):
    """Raised when image processing fails"""
    def __init__(self, message: str = "Failed to process the uploaded image. Please try with a different image."):
        super().__init__(message, "IMAGE_PROCESSING_ERROR")

class InvalidImageFormatError(AnalysisError):
    """Raised when the uploaded file is not a valid image format"""
    def __init__(self, message: str = "Invalid image format. Please upload a JPEG, PNG, or other supported image format."):
        super().__init__(message, "INVALID_IMAGE_FORMAT")

class RoutineData(BaseModel):
    sleep_hours: Optional[float] = None
    water_intake: Optional[int] = None  # glasses
    product_used: Optional[str] = None  # Keep for backward compatibility
    skincare_products: Optional[List[str]] = None  # New array for multiple products
    daily_note: Optional[str] = None

class FeatureScores(BaseModel):
    dark_circles: float = Field(..., ge=0, le=100)
    puffiness: float = Field(..., ge=0, le=100)
    brightness: float = Field(..., ge=0, le=100)
    wrinkles: float = Field(..., ge=0, le=100)
    texture: float = Field(..., ge=0, le=100)
    pore_size: float = Field(..., ge=0, le=100)

class AnalysisRequest(BaseModel):
    user_id: str
    routine_data: Optional[RoutineData] = None

class AnalysisResponse(BaseModel):
    user_id: str
    date: str
    sleep_score: int = Field(..., ge=0, le=100)
    skin_health_score: int = Field(..., ge=0, le=100)
    features: FeatureScores
    routine: Optional[RoutineData] = None
    fun_label: str
    confidence: float = Field(..., ge=0, le=1)
    smart_summary: Optional[Dict[str, Any]] = None

class UserData(BaseModel):
    user_id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    created_at: datetime
    last_active: datetime
    is_premium: bool = False
    streak_count: int = 0

class DailySummary(BaseModel):
    daily_summary: str
    sleep_score_change: Optional[int] = None
    skin_health_change: Optional[int] = None
    key_insights: List[str] = []
    recommendations: List[str] = []

class WeeklySummary(BaseModel):
    weekly_summary: str
    average_sleep_score: float
    average_skin_health_score: float
    score_trend: str  # "improving", "declining", "stable"
    lifestyle_insights: List[str] = []
    routine_effectiveness: List[str] = []

class RoutineSummary(BaseModel):
    routine_summary: str
    product_effectiveness: Dict[str, float] = {}
    lifestyle_correlations: Dict[str, float] = {}

class SocialSummary(BaseModel):
    social_summary: str
    shareable_card: Dict[str, Any] = {}

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Authentication Models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: str = Field(..., min_length=2, max_length=50)
    agree_to_terms: bool = Field(..., description="Must agree to terms and conditions")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    user_id: str
    email: str
    display_name: str
    is_premium: bool = False
    streak_count: int = 0
    created_at: datetime
    last_active: datetime
    profile_picture_url: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=50)
    profile_picture_url: Optional[str] = None
