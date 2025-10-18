from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime
from typing import Optional

app = FastAPI(
    title="Sleep Face API",
    description="AI-powered sleep and skin health tracking API",
    version="1.0.0"
)

# CORS middleware for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sleep Face API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze")
async def analyze_face(
    file: UploadFile = File(...),
    user_id: str = "guest",
    routine_data: Optional[str] = None
):
    """
    Analyze a selfie image and return sleep and skin health scores
    """
    try:
        # Parse routine data if provided
        routine = {}
        if routine_data:
            routine = json.loads(routine_data)
        
        # Return mock analysis result
        import random
        sleep_score = random.randint(30, 80)
        skin_score = random.randint(30, 80)
        
        fun_labels = [
            'Glow Queen 👑',
            'Glow Up 🌟',
            'Normal Day 😐',
            'Zombie Mode 🧟',
            'Sleepy Head 😴',
        ]
        
        result = {
            "user_id": user_id,
            "date": datetime.now().isoformat()[:10],
            "sleep_score": sleep_score,
            "skin_health_score": skin_score,
            "features": {
                "dark_circles": random.randint(-30, 30),
                "puffiness": random.randint(-30, 30),
                "brightness": random.randint(-30, 30),
                "wrinkles": random.randint(-30, 30),
                "texture": random.randint(-30, 30)
            },
            "routine": routine if routine else {
                "sleep_hours": random.randint(6, 10),
                "water_intake": random.randint(2, 8),
                "product_used": "Glow Cream",
                "daily_note": "Feeling good today!"
            },
            "fun_label": random.choice(fun_labels),
            "confidence": 0.85
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/user/{user_id}/history")
async def get_user_history(user_id: str, days: int = 7):
    """
    Get user's analysis history
    """
    try:
        # Return mock history
        import random
        history = []
        for i in range(min(days, 7)):
            date = datetime.now().replace(day=datetime.now().day-i)
            history.append({
                "user_id": user_id,
                "date": date.isoformat()[:10],
                "sleep_score": random.randint(30, 80),
                "skin_health_score": random.randint(30, 80),
                "fun_label": random.choice(['Glow Queen 👑', 'Normal Day 😐', 'Zombie Mode 🧟'])
            })
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@app.post("/user/{user_id}/summary")
async def generate_daily_summary(user_id: str, date: str):
    """
    Generate daily summary for user
    """
    try:
        # Return mock summary
        summary = {
            "daily_summary": "Your Sleep Score is 72 (+5 from yesterday). Your skin has a nice glow today! Dark circles improved slightly.",
            "sleep_score_change": 5,
            "skin_health_change": 3,
            "key_insights": [
                "Your skin has a nice glow today!",
                "Dark circles improved slightly",
                "Puffiness stayed stable"
            ],
            "recommendations": [
                "Keep up the good sleep routine",
                "Consider drinking more water",
                "Your skincare routine is working well"
            ]
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
