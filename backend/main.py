from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, date

from models import (
    AnalysisRequest, AnalysisResponse, UserData, DailySummary, AnalysisError, 
    NoFaceDetectedError, ImageProcessingError, InvalidImageFormatError,
    UserRegistration, UserLogin, UserProfile, AuthResponse, PasswordResetRequest, 
    PasswordReset, UserUpdate
)
from ai_engine import Core5Engine
from auth import verify_token
from database import get_database
from llm_service import FlexibleLLMService
from trend_analysis_service import trend_analysis_service
from historical_data_service import historical_data_service
from feature_correlation_analyzer import feature_correlation_analyzer
from weekly_analysis_service import weekly_analysis_service
from user_auth_service import UserAuthService
from smart_summary_service import smart_summary_service

# Load environment variables
load_dotenv()

# Initialize LLM service after environment variables are loaded
llm_service = FlexibleLLMService()

# Lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Set up MongoDB connection for historical_data_service
        db = await get_database()
        historical_data_service.set_database(db)
        print("✅ [STARTUP] Historical data service connected to MongoDB")
    except Exception as e:
        print(f"⚠️ [STARTUP] Failed to connect historical data service to MongoDB: {e}")
    
    yield
    
    # Shutdown (if needed)
    print("👋 [SHUTDOWN] Cleaning up...")

app = FastAPI(
    title="Sleep Face API",
    description="AI-powered sleep and skin health tracking API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize AI Engine
ai_engine = Core5Engine()

@app.get("/")
async def root():
    return {"message": "Sleep Face API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication Endpoints
@app.post("/auth/register", response_model=AuthResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        db = await get_database()
        auth_service = UserAuthService(db)
        return await auth_service.register_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """Authenticate user and return tokens"""
    try:
        db = await get_database()
        auth_service = UserAuthService(db)
        return await auth_service.login_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile"""
    try:
        # Verify token and get user data
        payload = verify_token(credentials)
        user_id = payload.get("uid") or payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = await get_database()
        auth_service = UserAuthService(db)
        user_profile = await auth_service.get_user_by_id(user_id)
        
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@app.put("/auth/profile", response_model=UserProfile)
async def update_user_profile(
    update_data: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user profile"""
    try:
        # Verify token and get user data
        payload = verify_token(credentials)
        user_id = payload.get("uid") or payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = await get_database()
        auth_service = UserAuthService(db)
        return await auth_service.update_user_profile(user_id, update_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.delete("/auth/delete-account")
async def delete_user_account(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Permanently delete user account and all associated data (GDPR/CCPA Compliance)"""
    try:
        # Verify token and get user data
        payload = verify_token(credentials)
        user_id = payload.get("uid") or payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"🗑️ [DELETE ACCOUNT] User {user_id} requested account deletion")
        
        db = await get_database()
        
        # Delete all user's analyses
        analyses_result = await db.analyses.delete_many({"user_id": user_id})
        print(f"🗑️ [DELETE ACCOUNT] Deleted {analyses_result.deleted_count} analyses")
        
        # Delete all user's sessions
        sessions_result = await db.sessions.delete_many({"user_id": user_id})
        print(f"🗑️ [DELETE ACCOUNT] Deleted {sessions_result.deleted_count} sessions")
        
        # Delete user document
        user_result = await db.users.delete_one({"user_id": user_id})
        print(f"🗑️ [DELETE ACCOUNT] Deleted user account")
        
        # Delete local JSON history file if exists
        try:
            import os
            from pathlib import Path
            history_file = Path(f"data/{user_id}_history.json")
            if history_file.exists():
                os.remove(history_file)
                print(f"🗑️ [DELETE ACCOUNT] Deleted local history file")
        except Exception as e:
            print(f"⚠️ [DELETE ACCOUNT] Could not delete local history: {e}")
        
        return {
            "success": True,
            "message": "Account and all data permanently deleted",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [DELETE ACCOUNT] Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")

@app.post("/auth/refresh", response_model=AuthResponse)
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    try:
        db = await get_database()
        auth_service = UserAuthService(db)
        return await auth_service.refresh_access_token(refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh token: {str(e)}")

@app.post("/auth/logout")
async def logout_user(refresh_token: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user by invalidating refresh token"""
    try:
        # Verify token and get user data
        payload = verify_token(credentials)
        user_id = payload.get("uid") or payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = await get_database()
        auth_service = UserAuthService(db)
        success = await auth_service.logout_user(user_id, refresh_token)
        
        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(status_code=400, detail="Failed to logout")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@app.get("/models/available")
async def get_available_models():
    """Get list of available LLM models"""
    try:
        available_models = llm_service.get_available_models()
        return {
            "available_models": [model.value for model in available_models],
            "current_priority": [model.value for model in llm_service.model_priority],
            "total_models": len(available_models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@app.post("/models/priority")
async def set_model_priority(priority: List[str]):
    """Set the priority order for model selection"""
    try:
        from llm_service import ModelType
        
        # Convert string names to ModelType enums
        model_types = []
        for model_name in priority:
            try:
                model_type = ModelType(model_name)
                model_types.append(model_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid model type: {model_name}")
        
        llm_service.set_model_priority(model_types)
        return {
            "message": "Model priority updated successfully",
            "new_priority": [model.value for model in model_types]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set priority: {str(e)}")

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_face(
    file: UploadFile = File(...),
    user_id: str = "guest",
    routine_data: Optional[str] = None
):
    """
    Analyze a selfie image and return sleep and skin health scores
    """
    try:
        print(f"🚀 [API] Received analysis request from user: {user_id}")
        print(f"📁 [API] File: {file.filename}, Content type: {file.content_type}")
        print(f"📊 [API] Routine data: {routine_data}")
        
        # Read image data
        image_data = await file.read()
        print(f"📸 [API] Image data size: {len(image_data)} bytes")
        
        # Parse routine data if provided
        routine = {}
        if routine_data:
            routine = json.loads(routine_data)
            print(f"📋 [API] Parsed routine data: {routine}")
        
        print("🤖 [API] Starting AI analysis...")
        # Run AI analysis
        analysis_result = await ai_engine.analyze_image(image_data, user_id, routine)
        
        print(f"✅ [API] Analysis complete! Sleep: {analysis_result.sleep_score}, Skin: {analysis_result.skin_health_score}")
        
        # Generate data-driven smart summary
        try:
            print("🧠 [API] Generating data-driven smart summary...")
            analysis_data = {
                "user_id": analysis_result.user_id,
                "date": analysis_result.date,
                "sleep_score": analysis_result.sleep_score,
                "skin_health_score": analysis_result.skin_health_score,
                "features": analysis_result.features.model_dump(),
                "routine": routine
            }
            
            # Get historical data for trend analysis (skip for guest users)
            historical_data = []
            if user_id != "guest":
                historical_data = await historical_data_service.get_user_history(user_id, 30)
                print(f"📊 [HISTORICAL DATA] Retrieved {len(historical_data)} entries for user {user_id}")
            else:
                print(f"👤 [HISTORICAL DATA] Skipping historical data for guest user")
            
            # Use data-driven smart summary service (no LLM dependency)
            smart_summary = await smart_summary_service.generate_smart_summary(
                analysis_data, 
                routine, 
                historical_data
            )
            
            if smart_summary:
                print(f"✨ [API] Data-driven summary generated: {smart_summary.get('daily_summary', 'N/A')[:80]}...")
                # Add smart summary to the response
                analysis_result.smart_summary = smart_summary
            else:
                print(f"⚠️ [API] Smart summary is None, skipping")
            
        except Exception as e:
            print(f"⚠️ [API] Smart summary generation failed: {e}")
            # Continue without smart summary
        
        # Save data ONLY for registered users (NOT for guests)
        if user_id != "guest":
            try:
                # Save to MongoDB for persistent storage and historical analysis
                db = await get_database()
                mongo_data = {
                    "user_id": analysis_result.user_id,
                    "date": analysis_result.date,
                    "sleep_score": analysis_result.sleep_score,
                    "skin_health_score": analysis_result.skin_health_score,
                    "features": analysis_result.features.model_dump(),
                    "routine": routine,
                    "confidence": analysis_result.confidence,
                    "fun_label": analysis_result.fun_label,
                    "smart_summary": smart_summary,
                    "created_at": datetime.now()
                }
                from database import save_analysis
                await save_analysis(db, mongo_data)
                print(f"💾 [MONGODB] Analysis saved to database for registered user {analysis_result.user_id}")
                
                # Also save to local JSON for quick trend analysis
                historical_data = {
                    "user_id": analysis_result.user_id,
                    "date": analysis_result.date,
                    "sleep_score": analysis_result.sleep_score,
                    "skin_health_score": analysis_result.skin_health_score,
                    "features": analysis_result.features.model_dump(),
                    "routine": routine
                }
                historical_data_service.save_analysis_data(analysis_result.user_id, historical_data)
                print(f"💾 [LOCAL] Historical data cached locally for trend analysis")
            except Exception as e:
                print(f"⚠️ [STORAGE] Failed to save data for registered user: {e}")
                # Continue without saving
        else:
            print(f"👤 [GUEST] Skipping data storage for guest user (no persistence)")
        
        print(f"✅ [API] Returning complete result")
        return analysis_result
        
    except NoFaceDetectedError as e:
        print(f"❌ [API] No face detected: {e.message}")
        raise HTTPException(status_code=400, detail={
            "error": e.error_code,
            "message": e.message,
            "suggestion": "Please upload a clear selfie with your face visible. Make sure your face is well-lit and not obscured."
        })
    except InvalidImageFormatError as e:
        print(f"❌ [API] Invalid image format: {e.message}")
        raise HTTPException(status_code=400, detail={
            "error": e.error_code,
            "message": e.message,
            "suggestion": "Please upload a JPEG, PNG, or other supported image format."
        })
    except ImageProcessingError as e:
        print(f"❌ [API] Image processing error: {e.message}")
        raise HTTPException(status_code=400, detail={
            "error": e.error_code,
            "message": e.message,
            "suggestion": "Please try with a different image or check if the file is corrupted."
        })
    except AnalysisError as e:
        print(f"❌ [API] Analysis error: {e.message}")
        raise HTTPException(status_code=400, detail={
            "error": e.error_code,
            "message": e.message
        })
    except Exception as e:
        print(f"❌ [API] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred during analysis. Please try again later."
        })

@app.get("/user/{user_id}/history")
async def get_user_history(
    user_id: str,
    days: int = 7
):
    """
    Get user's analysis history
    Returns empty array for first-time users (not an error)
    Works for both authenticated users and guest users
    NO AUTHENTICATION REQUIRED - open endpoint
    """
    try:
        # No auth required for this endpoint
        print(f"📊 [API] Fetching history for user {user_id} (no auth required)")
        
        print(f"📊 [API] Fetching {days}-day history for user {user_id}")
        
        # Guest users - return empty history from local storage hint
        if user_id == "guest":
            print(f"👤 [API] Guest user - returning empty history (check local storage)")
            return {
                "history": [],
                "is_first_time": True,
                "is_guest": True,
                "message": "Guest users - history stored locally on device only"
            }
        
        # Get database for registered users
        db = await get_database()
        
        # Query user history
        collection = db["analyses"]
        cursor = collection.find(
            {"user_id": user_id}
        ).sort("date", -1).limit(days)
        
        history = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            history.append(doc)
        
        # First-time users will have empty history - this is normal!
        if len(history) == 0:
            print(f"✅ [API] No history yet for user {user_id} (new user)")
        else:
            print(f"✅ [API] Found {len(history)} historical entries for user {user_id}")
        
        return {
            "history": history,
            "is_first_time": len(history) == 0,
            "is_guest": False,
            "message": "Take your first selfie to start tracking!" if len(history) == 0 else f"Found {len(history)} entries"
        }
        
    except Exception as e:
        print(f"⚠️ [API] History fetch error: {str(e)}")
        # Return empty history instead of error for first-time users
        return {
            "history": [],
            "is_first_time": True,
            "is_guest": user_id == "guest",
            "message": "No history available yet - take your first selfie!",
            "error": str(e)
        }

@app.get("/user/{user_id}/summary")
async def get_daily_summary(
    user_id: str,
    date: str = None
):
    """
    Get daily summary for user (no auth required for guest users)
    """
    try:
        # Use today's date if not provided
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        print(f"📊 Generating smart summary for user {user_id} on {date}")

        # Get historical data for ultra-smart analysis (skip for guest users)
        historical_data = []
        if user_id != "guest":
            historical_data = await historical_data_service.get_user_history(user_id, 30)
            print(f"📊 [HISTORICAL DATA] Retrieved {len(historical_data)} entries for user {user_id}")
        else:
            print(f"👤 [HISTORICAL DATA] Skipping historical data for guest user")
        
        # Get the most recent analysis for this date (today's selfie analysis)
        today_analysis = None
        if historical_data:
            # Find the most recent analysis for the specific date
            # (since there might be multiple entries for the same date)
            matching_entries = [entry for entry in historical_data if entry.get('date') == date]
            if matching_entries:
                # Get the most recent entry (last one in the list)
                today_analysis = matching_entries[-1]
                print(f"📊 Found {len(matching_entries)} entries for {date}, using most recent: Sleep {today_analysis.get('sleep_score')}, Skin {today_analysis.get('skin_health_score')}")
        
        # If no analysis for today, use the most recent analysis
        if not today_analysis and historical_data:
            today_analysis = historical_data[-1]
            print(f"⚠️ No analysis found for {date}, using most recent analysis")
        
        # If no historical data at all, use mock data
        if not today_analysis:
            print(f"⚠️ No historical data found for {user_id}, using mock data")
            today_analysis = {
                "user_id": user_id,
                "date": date,
                "sleep_score": 65,
                "skin_health_score": 70,
                "features": {
                    "dark_circles": -25,
                    "puffiness": -15,
                    "brightness": 20,
                    "wrinkles": -10,
                    "texture": 15
                },
                "routine": {
                    "sleep_hours": 7.5,
                    "water_intake": 6,
                    "product_used": "Vitamin C serum, moisturizer",
                    "daily_note": "Feeling good today"
                }
            }

        # Generate data-driven summary with trend analysis
        summary = await smart_summary_service.generate_smart_summary(
            today_analysis,  # Current analysis from today's selfie
            today_analysis.get("routine", {}),
            historical_data  # Historical data for trend analysis
        )

        print(f"✅ Data-driven summary generated: {summary['daily_summary'][:80]}...")
        return summary

    except Exception as e:
        print(f"❌ Error generating smart summary: {e}")
        # Fallback to basic summary
        return {
            "daily_summary": f"Your analysis for {date} shows areas for improvement. Focus on getting better sleep and maintaining a consistent skincare routine.",
            "key_insights": [
                "Take your first selfie to get personalized insights!"
            ],
            "recommendations": [
                "Take your first selfie to get personalized recommendations!"
            ]
        }

@app.post("/user/{user_id}/summary")
async def generate_daily_summary(
    user_id: str,
    date: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate daily summary for user
    """
    try:
        # Verify token
        await verify_token(credentials.credentials)
        
        # Get database
        db = await get_database()
        
        # Get today's and yesterday's data
        collection = db["analyses"]
        today = datetime.fromisoformat(date)
        yesterday = today.replace(day=today.day-1) if today.day > 1 else None
        
        today_data = await collection.find_one({
            "user_id": user_id,
            "date": today.isoformat()[:10]
        })
        
        yesterday_data = None
        if yesterday:
            yesterday_data = await collection.find_one({
                "user_id": user_id,
                "date": yesterday.isoformat()[:10]
            })
        
        # Generate summary
        summary = await ai_engine.generate_daily_summary(today_data, yesterday_data)
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@app.post("/user/{user_id}/weekly-summary")
async def generate_weekly_summary(
    user_id: str,
    week_start: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate weekly summary for user
    """
    try:
        # Verify token
        await verify_token(credentials.credentials)
        
        # Get database
        db = await get_database()
        
        # Get week's data
        collection = db["analyses"]
        start_date = datetime.fromisoformat(week_start)
        
        cursor = collection.find({
            "user_id": user_id,
            "date": {
                "$gte": start_date.isoformat()[:10],
                "$lt": (start_date.replace(day=start_date.day+7)).isoformat()[:10]
            }
        }).sort("date", 1)
        
        week_data = []
        async for doc in cursor:
            week_data.append(doc)
        
        # Generate summary
        summary = await ai_engine.generate_weekly_summary(week_data)
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weekly summary: {str(e)}")

@app.get("/user/{user_id}/trend-analysis")
async def get_trend_analysis(
    user_id: str,
    days: int = 30
):
    """
    Get comprehensive trend analysis for a user's skincare routine effectiveness
    """
    try:
        print(f"📊 [API] Getting trend analysis for user: {user_id}, days: {days}")
        
        # Get historical data
        historical_data = await historical_data_service.get_user_history(user_id, days)
        
        if not historical_data:
            return {
                "insufficient_data": True,
                "message": f"No data available for trend analysis. Need at least 3 data points.",
                "current_data_points": 0
            }
        
        # Perform trend analysis
        trend_analysis = await trend_analysis_service.analyze_routine_effectiveness(user_id, historical_data)
        
        print(f"✅ [API] Trend analysis completed for user: {user_id}")
        return trend_analysis
        
    except Exception as e:
        print(f"❌ [API] Trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate trend analysis: {str(e)}")

@app.get("/user/{user_id}/product-effectiveness")
async def get_product_effectiveness(
    user_id: str,
    product_id: str = None,
    days: int = 30
):
    """
    Get effectiveness analysis for specific products or all products
    """
    try:
        print(f"🔍 [API] Getting product effectiveness for user: {user_id}, product: {product_id}")
        
        # Get historical data
        historical_data = await historical_data_service.get_user_history(user_id, days)
        
        if not historical_data:
            return {
                "insufficient_data": True,
                "message": "No data available for product effectiveness analysis"
            }
        
        # Analyze product effectiveness
        trend_analysis = await trend_analysis_service.analyze_routine_effectiveness(user_id, historical_data)
        
        if product_id:
            # Filter for specific product
            product_effectiveness = [
                product for product in trend_analysis.get('product_effectiveness', [])
                if product.get('product_id') == product_id
            ]
            return {
                "product_id": product_id,
                "effectiveness": product_effectiveness[0] if product_effectiveness else None
            }
        else:
            # Return all products
            return {
                "product_effectiveness": trend_analysis.get('product_effectiveness', []),
                "analysis_period": trend_analysis.get('analysis_period', {})
            }
        
    except Exception as e:
        print(f"❌ [API] Product effectiveness analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze product effectiveness: {str(e)}")

@app.get("/user/{user_id}/routine-insights")
async def get_routine_insights(
    user_id: str,
    days: int = 30
):
    """
    Get AI-generated insights about routine effectiveness and recommendations
    """
    try:
        print(f"💡 [API] Getting routine insights for user: {user_id}, days: {days}")
        
        # Get historical data
        historical_data = await historical_data_service.get_user_history(user_id, days)
        
        if not historical_data:
            return {
                "insufficient_data": True,
                "message": "No data available for routine insights"
            }
        
        # Get trend analysis
        trend_analysis = await trend_analysis_service.analyze_routine_effectiveness(user_id, historical_data)
        
        return {
            "routine_insights": trend_analysis.get('routine_insights', []),
            "recommendations": trend_analysis.get('recommendations', []),
            "overall_trends": trend_analysis.get('overall_trends', {}),
            "analysis_period": trend_analysis.get('analysis_period', {})
        }
        
    except Exception as e:
        print(f"❌ [API] Routine insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate routine insights: {str(e)}")

@app.get("/user/{user_id}/statistics")
async def get_user_statistics(
    user_id: str,
    days: int = 30
):
    """
    Get user's overall statistics and trends
    """
    try:
        print(f"📈 [API] Getting statistics for user: {user_id}, days: {days}")
        
        # Get statistics from historical data service
        statistics = historical_data_service.get_user_statistics(user_id, days)
        
        return statistics
        
    except Exception as e:
        print(f"❌ [API] Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user statistics: {str(e)}")

@app.get("/user/{user_id}/smart-analysis")
async def get_smart_analysis(
    user_id: str,
    days: int = 30
):
    """
    Get ultra-smart analysis correlating specific products with facial feature improvements
    """
    try:
        print(f"🧠 [API] Getting smart analysis for user: {user_id}, days: {days}")
        
        # Get historical data
        historical_data = await historical_data_service.get_user_history(user_id, days)
        
        if not historical_data:
            return {
                "insufficient_data": True,
                "message": "No data available for smart analysis. Need at least 3 data points.",
                "current_data_points": 0
            }
        
        # Perform advanced feature correlation analysis
        smart_analysis = feature_correlation_analyzer.analyze_feature_product_correlations(historical_data)
        
        print(f"✅ [API] Smart analysis completed for user: {user_id}")
        return smart_analysis
        
    except Exception as e:
        print(f"❌ [API] Smart analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate smart analysis: {str(e)}")

@app.get("/user/{user_id}/feature-improvements")
async def get_feature_improvements(
    user_id: str,
    feature: str = None,
    days: int = 30
):
    """
    Get detailed analysis of specific facial feature improvements
    """
    try:
        print(f"📊 [API] Getting feature improvements for user: {user_id}, feature: {feature}")
        
        # Get historical data
        historical_data = await historical_data_service.get_user_history(user_id, days)
        
        if not historical_data:
            return {
                "insufficient_data": True,
                "message": "No data available for feature analysis"
            }
        
        # Get smart analysis
        smart_analysis = feature_correlation_analyzer.analyze_feature_product_correlations(historical_data)
        
        if feature:
            # Filter for specific feature
            feature_improvements = [
                imp for imp in smart_analysis.get('feature_improvements', [])
                if imp.get('feature') == feature
            ]
            return {
                "feature": feature,
                "improvement": feature_improvements[0] if feature_improvements else None
            }
        else:
            # Return all features
            return {
                "feature_improvements": smart_analysis.get('feature_improvements', []),
                "analysis_period": smart_analysis.get('analysis_period', {})
            }
        
    except Exception as e:
        print(f"❌ [API] Feature improvements analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze feature improvements: {str(e)}")

@app.get("/user/{user_id}/product-effectiveness-detailed")
async def get_detailed_product_effectiveness(
    user_id: str,
    product_id: str = None,
    days: int = 30
):
    """
    Get detailed product effectiveness analysis with feature-specific impacts
    """
    try:
        print(f"🔍 [API] Getting detailed product effectiveness for user: {user_id}, product: {product_id}")
        
        # Get historical data
        historical_data = await historical_data_service.get_user_history(user_id, days)
        
        if not historical_data:
            return {
                "insufficient_data": True,
                "message": "No data available for detailed product analysis"
            }
        
        # Get smart analysis
        smart_analysis = feature_correlation_analyzer.analyze_feature_product_correlations(historical_data)
        
        if product_id:
            # Filter for specific product
            product_impacts = [
                impact for impact in smart_analysis.get('product_impacts', [])
                if impact.get('product_id') == product_id
            ]
            return {
                "product_id": product_id,
                "detailed_impact": product_impacts[0] if product_impacts else None
            }
        else:
            # Return all products
            return {
                "product_impacts": smart_analysis.get('product_impacts', []),
                "trust_metrics": smart_analysis.get('trust_metrics', {}),
                "analysis_period": smart_analysis.get('analysis_period', {})
            }
        
    except Exception as e:
        print(f"❌ [API] Detailed product effectiveness analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze detailed product effectiveness: {str(e)}")

@app.get("/user/{user_id}/weekly-analysis")
async def get_weekly_analysis(
    user_id: str,
    days: int = 7
):
    """
    Get comprehensive weekly analysis with trends and insights
    """
    try:
        print(f"📊 [API] Getting weekly analysis for {user_id}")
        
        # Get weekly analysis
        weekly_analysis = await weekly_analysis_service.get_weekly_analysis(user_id, days)
        
        print(f"✅ [API] Weekly analysis complete")
        return weekly_analysis
        
    except Exception as e:
        print(f"❌ [API] Weekly analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get weekly analysis: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
