# Sleep Face Backend 🚀

AI-powered backend API for Sleep Face mobile app - analyzing sleep quality and skin health from selfies.

## 🎯 Overview

This is the Python FastAPI backend that powers the Sleep Face mobile application. It uses computer vision and machine learning to analyze facial features and provide insights on sleep quality and skin health.

## ✨ Features

### 🤖 AI Engine
- **Face Detection**: MediaPipe FaceMesh for accurate landmark detection
- **6 Feature Analysis**:
  - Dark Circles (0-100 score)
  - Eye Puffiness (0-100 score)
  - Skin Brightness (0-100 score)
  - Fine Lines/Wrinkles (0-100 score)
  - Skin Texture (0-100 score)
  - Pore Size (0-100 score)
- **Smart Scoring**: Sleep Score & Skin Health Score calculation
- **Data-Driven Summaries**: Trend analysis without LLM dependencies

### 📊 Data & Analytics
- **Historical Tracking**: 30-day data storage per user
- **Trend Analysis**: 7-day vs 7-day comparison
- **Stagnation Detection**: 14-day monitoring for plateaued features
- **Product Effectiveness**: Track which skincare products work best
- **Feature Correlation**: AI-powered product-to-feature analysis

### 🔐 Authentication
- Firebase Authentication integration
- JWT token validation
- User profile management
- Guest mode support

## 🏗️ Architecture

```
backend/
├── main.py                          # FastAPI application & routes
├── ai_engine.py                     # Core CV/ML analysis engine
├── models.py                        # Pydantic data models
├── auth.py                          # Firebase authentication
├── database.py                      # MongoDB operations
├── smart_summary_service.py         # Data-driven summary generation (NEW!)
├── llm_service.py                   # LLM fallback (optional)
├── historical_data_service.py       # Data storage & retrieval
├── trend_analysis_service.py        # Product effectiveness analysis
├── feature_correlation_analyzer.py  # Feature-product correlation
├── weekly_analysis_service.py       # Weekly trend reports
├── user_auth_service.py            # User authentication service
├── config.py                        # Configuration management
├── requirements.txt                 # Python dependencies
├── env.example                      # Environment template
├── data/                            # User historical data (JSON)
└── models/                          # ML models (.tflite files)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- Firebase project (for authentication)

### Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up Firebase** (Optional - for authentication)
   - Create Firebase project at https://console.firebase.google.com
   - Download service account key as `serviceAccountKey.json`
   - Place in backend directory
   - Update `.env` with Firebase credentials

6. **Set up MongoDB** (Optional - for production)
   - Install MongoDB or use MongoDB Atlas
   - Update `MONGO_URL` in `.env`
   - Default uses local JSON storage in `data/` directory

### Running

#### Development Mode
```bash
python main.py
```

Server starts at: **http://localhost:8000**

#### With Uvicorn (Production)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Check Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T10:30:00.123456"
}
```

## 📡 API Endpoints

### Core Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze selfie image with routine data |
| `/user/{user_id}/summary` | GET | Get daily summary with trends |
| `/user/{user_id}/history` | GET | Get analysis history (7-30 days) |

### Trend & Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/user/{user_id}/trend-analysis` | GET | Routine effectiveness analysis |
| `/user/{user_id}/smart-analysis` | GET | Feature-product correlations |
| `/user/{user_id}/weekly-analysis` | GET | Weekly trends and insights |
| `/user/{user_id}/statistics` | GET | User statistics summary |

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login user |
| `/auth/me` | GET | Get current user profile |
| `/auth/refresh` | POST | Refresh access token |

### System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/models/available` | GET | List available LLM models |

## 🧪 Testing

### Test Image Analysis
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@test_face.jpg" \
  -F "user_id=test_user_123" \
  -F 'routine_data={"sleep_hours": 7, "water_intake": 8, "skincare_products": ["vitamin_c", "retinol"]}'
```

### Test Summary Generation
```bash
curl http://localhost:8000/user/guest/summary
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `env.example`):

```env
# Database
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=sleepface

# Firebase (Optional)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-client-email

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# LLM (Optional)
OPENAI_API_KEY=your-openai-api-key
XAI_API_KEY=your-xai-grok-api-key
```

## 📊 Data-Driven Smart Summary (NEW!)

The backend now uses **purely data-driven analysis** instead of unreliable LLM APIs:

### 5-Step Methodology

1. **Data Collection**: Historical data stored in JSON files
2. **Trend Analysis**: 7-day vs 7-day statistical comparison
3. **Change Detection**: Thresholds for improvement/decline/stagnation
4. **Duration Monitoring**: 14-day stagnation detection
5. **Summary Generation**: Rule-based insights and recommendations

### Example Output

```json
{
  "daily_summary": "Good progress! Sleep Score: 84, Skin Health: 78. You're seeing positive changes in 3 areas. Stay consistent! 💪",
  "key_insights": [
    "🎉 Brightness improved by 8.2 points (11%) - your efforts are paying off!",
    "🔄 Pore Size hasn't improved in 2+ weeks - consider trying different products"
  ],
  "recommendations": [
    "🔍 Pore Size stagnant - try niacinamide serum or salicylic acid cleanser",
    "✅ Continue your current routine - it's working well for Brightness!"
  ],
  "trend_analysis": {
    "improving_features": ["brightness", "texture"],
    "stagnant_features": ["pore_size"]
  },
  "model": "Data-Driven Analysis",
  "data_points_analyzed": 16
}
```

**Benefits:**
- ✅ 100% reliable (no API failures)
- ✅ <100ms response time
- ✅ Privacy-focused (no external data sharing)
- ✅ Accurate user-specific insights

See `DATA_DRIVEN_SUMMARY_IMPLEMENTATION.md` for complete documentation.

## 🤖 AI Engine Details

### Computer Vision Pipeline

1. **Image Preprocessing**
   - CLAHE lighting normalization
   - Bilateral filtering (noise reduction)
   - Skin tone normalization

2. **Face Detection**
   - MediaPipe FaceMesh (478 landmarks)
   - Confidence threshold: 0.5

3. **Feature Extraction** (per feature)
   - **Dark Circles**: Brightness analysis, dark pixel ratio, texture variance
   - **Puffiness**: Gradient magnitude, Laplacian variance, contour roundness
   - **Brightness**: LAB color space, skin tone evenness, distribution analysis
   - **Wrinkles**: Canny/Sobel edge detection, morphological operations
   - **Texture**: LBP analysis, Gabor filters, gradient calculations
   - **Pore Size**: Multi-scale detection, contour analysis, circularity

4. **Score Calculation**
   - Sleep Score: Weighted average of dark_circles, puffiness, brightness
   - Skin Health Score: Weighted average of all 6 features
   - Lifestyle adjustments (±10 points for sleep, water, products)

### Model Files

Place trained models in `models/` directory:
- `dark_circles.tflite`
- `puffiness.tflite`
- `brightness.tflite`
- `wrinkles.tflite`
- `texture.tflite`

**Note**: System falls back to enhanced heuristics if models not found.

## 🗄️ Data Storage

### Local JSON Storage

User data stored in `data/{user_id}_history.json`:

```json
[
  {
    "date": "2025-10-16",
    "sleep_score": 84,
    "skin_health_score": 78,
    "features": {
      "dark_circles": 65.2,
      "puffiness": 58.4,
      ...
    },
    "routine": {
      "sleep_hours": 7.5,
      "water_intake": 8,
      "skincare_products": ["vitamin_c", "retinol"]
    },
    "timestamp": "2025-10-16T08:16:03.620514"
  }
]
```

### MongoDB (Optional)

For production, configure MongoDB Atlas:
1. Create cluster at https://cloud.mongodb.com
2. Get connection string
3. Update `MONGO_URL` in `.env`

## 🔒 Security

- Firebase JWT token validation
- CORS middleware configured
- Sensitive data in `.env` (gitignored)
- Input validation with Pydantic
- Image size limits (prevent DoS)

## 📈 Performance

- **Image Analysis**: <2 seconds
- **Summary Generation**: <100ms (data-driven)
- **Historical Data Retrieval**: <50ms

## 🐛 Debugging

Enable detailed logging:
```python
# In main.py
DEBUG=True
```

Check logs for:
- `🔍 [AI ENGINE]` - Computer vision processing
- `📊 [HISTORICAL DATA]` - Data operations
- `🧠 [SMART SUMMARY]` - Summary generation
- `✅ [API]` - Request/response flow

## 📚 Documentation

- [Data-Driven Summary Implementation](../DATA_DRIVEN_SUMMARY_IMPLEMENTATION.md)
- [API Documentation](http://localhost:8000/docs) - Swagger UI
- [ReDoc](http://localhost:8000/redoc) - Alternative API docs

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test with sample images
4. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues or questions:
- Create GitHub issue
- Email: support@sleepface.app

---

**Made with ❤️ for better sleep and skin health**

