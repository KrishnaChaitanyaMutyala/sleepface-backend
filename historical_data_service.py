from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

class HistoricalDataService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db = None  # Will be set by main.py
    
    def set_database(self, db):
        """Set MongoDB database instance for registered user data retrieval"""
        self.db = db
        
    def save_analysis_data(self, user_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Save analysis data to historical storage"""
        try:
            user_file = self.data_dir / f"{user_id}_history.json"
            
            # Load existing data
            if user_file.exists():
                with open(user_file, 'r') as f:
                    historical_data = json.load(f)
            else:
                historical_data = []
            
            # Add new analysis data
            historical_data.append({
                'date': analysis_data.get('date'),
                'sleep_score': analysis_data.get('sleep_score'),
                'skin_health_score': analysis_data.get('skin_health_score'),
                'features': analysis_data.get('features', {}),
                'routine': analysis_data.get('routine', {}),
                'timestamp': datetime.now().isoformat()
            })
            
            # Save updated data
            with open(user_file, 'w') as f:
                json.dump(historical_data, f, indent=2)
            
            print(f"💾 [HISTORICAL DATA] Saved analysis data for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ [HISTORICAL DATA] Error saving data: {e}")
            return False
    
    async def get_user_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user's historical data for the specified number of days
        
        For registered users: Retrieves from MongoDB (persistent storage)
        For guest users: Retrieves from local JSON (temporary cache)
        """
        try:
            # For registered users, retrieve from MongoDB
            if user_id != "guest" and not user_id.startswith("guest_") and self.db is not None:
                try:
                    from database import get_user_analyses
                    
                    # Get analyses from MongoDB
                    analyses = await get_user_analyses(self.db, user_id, limit=days)
                    
                    # Convert MongoDB documents to the format expected by analysis
                    historical_data = []
                    for analysis in analyses:
                        historical_data.append({
                            'date': analysis.get('date'),
                            'sleep_score': analysis.get('sleep_score'),
                            'skin_health_score': analysis.get('skin_health_score'),
                            'features': analysis.get('features', {}),
                            'routine': analysis.get('routine', {}),
                            'timestamp': analysis.get('created_at', datetime.now()).isoformat() if isinstance(analysis.get('created_at'), datetime) else str(analysis.get('created_at', datetime.now().isoformat()))
                        })
                    
                    # Filter by date range
                    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()[:10]
                    filtered_data = [
                        entry for entry in historical_data 
                        if entry.get('date', '') >= cutoff_date
                    ]
                    
                    print(f"📊 [MONGODB] Retrieved {len(filtered_data)} entries for registered user {user_id}")
                    return filtered_data
                    
                except Exception as mongo_error:
                    print(f"⚠️ [MONGODB] Error retrieving from MongoDB: {mongo_error}, falling back to local JSON")
                    # Fall through to local JSON as backup
            
            # For guest users or fallback, use local JSON files
            user_file = self.data_dir / f"{user_id}_history.json"
            
            if not user_file.exists():
                print(f"📊 [LOCAL JSON] No historical data file found for user {user_id}")
                return []
            
            with open(user_file, 'r') as f:
                historical_data = json.load(f)
            
            # Filter by date range
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()[:10]
            filtered_data = [
                entry for entry in historical_data 
                if entry.get('date', '') >= cutoff_date
            ]
            
            print(f"📊 [LOCAL JSON] Retrieved {len(filtered_data)} entries for user {user_id}")
            return filtered_data
            
        except Exception as e:
            print(f"❌ [HISTORICAL DATA] Error retrieving data: {e}")
            return []
    
    def get_user_history_by_date_range(self, user_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get user's historical data for a specific date range"""
        try:
            user_file = self.data_dir / f"{user_id}_history.json"
            
            if not user_file.exists():
                return []
            
            with open(user_file, 'r') as f:
                historical_data = json.load(f)
            
            # Filter by date range
            filtered_data = [
                entry for entry in historical_data 
                if start_date <= entry.get('date', '') <= end_date
            ]
            
            print(f"📊 [HISTORICAL DATA] Retrieved {len(filtered_data)} entries for user {user_id} from {start_date} to {end_date}")
            return filtered_data
            
        except Exception as e:
            print(f"❌ [HISTORICAL DATA] Error retrieving data: {e}")
            return []
    
    def get_user_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user's statistics summary"""
        historical_data = self.get_user_history(user_id, days)
        
        if not historical_data:
            return {
                "total_entries": 0,
                "avg_sleep_score": 0,
                "avg_skin_score": 0,
                "best_sleep_score": 0,
                "best_skin_score": 0,
                "improvement_trend": "no_data"
            }
        
        sleep_scores = [entry.get('sleep_score', 0) for entry in historical_data]
        skin_scores = [entry.get('skin_health_score', 0) for entry in historical_data]
        
        # Calculate trends
        if len(sleep_scores) >= 4:
            recent_sleep = sum(sleep_scores[-4:]) / 4
            early_sleep = sum(sleep_scores[:4]) / 4
            sleep_trend = "improving" if recent_sleep > early_sleep + 5 else "declining" if recent_sleep < early_sleep - 5 else "stable"
        else:
            sleep_trend = "insufficient_data"
        
        if len(skin_scores) >= 4:
            recent_skin = sum(skin_scores[-4:]) / 4
            early_skin = sum(skin_scores[:4]) / 4
            skin_trend = "improving" if recent_skin > early_skin + 5 else "declining" if recent_skin < early_skin - 5 else "stable"
        else:
            skin_trend = "insufficient_data"
        
        return {
            "total_entries": len(historical_data),
            "avg_sleep_score": round(sum(sleep_scores) / len(sleep_scores), 1),
            "avg_skin_score": round(sum(skin_scores) / len(skin_scores), 1),
            "best_sleep_score": max(sleep_scores),
            "best_skin_score": max(skin_scores),
            "sleep_trend": sleep_trend,
            "skin_trend": skin_trend,
            "date_range": {
                "start": historical_data[0].get('date'),
                "end": historical_data[-1].get('date')
            }
        }
    
    def cleanup_old_data(self, user_id: str, days_to_keep: int = 90) -> bool:
        """Clean up old data beyond the specified days"""
        try:
            user_file = self.data_dir / f"{user_id}_history.json"
            
            if not user_file.exists():
                return True
            
            with open(user_file, 'r') as f:
                historical_data = json.load(f)
            
            # Filter to keep only recent data
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()[:10]
            filtered_data = [
                entry for entry in historical_data 
                if entry.get('date', '') >= cutoff_date
            ]
            
            # Save filtered data
            with open(user_file, 'w') as f:
                json.dump(filtered_data, f, indent=2)
            
            print(f"🧹 [HISTORICAL DATA] Cleaned up old data for user {user_id}, kept {len(filtered_data)} entries")
            return True
            
        except Exception as e:
            print(f"❌ [HISTORICAL DATA] Error cleaning up data: {e}")
            return False

# Global instance
historical_data_service = HistoricalDataService()
