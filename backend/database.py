import motor.motor_asyncio
import os
from typing import Optional
from pymongo import MongoClient
import asyncio
from config import MONGO_URL, DATABASE_NAME, is_production, is_development

# Database configuration
# MONGO_URL and DATABASE_NAME are now imported from config.py

# Database name is set by environment configuration
# No need to parse from URL since we use explicit DATABASE_NAME

# Global database instance
_database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

async def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """
    Get database instance
    """
    global _database
    
    if _database is None:
        # Create MongoDB client
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        _database = client[DATABASE_NAME]
        
        # Create indexes
        await create_indexes(_database)
    
    return _database

async def create_indexes(db: motor.motor_asyncio.AsyncIOMotorDatabase):
    """
    Create database indexes for better performance
    """
    try:
        # Analyses collection indexes
        await db.analyses.create_index([("user_id", 1), ("date", -1)])
        await db.analyses.create_index([("user_id", 1), ("created_at", -1)])
        
        # Users collection indexes
        await db.users.create_index([("user_id", 1)], unique=True)
        await db.users.create_index([("email", 1)], unique=True, sparse=True)
        
        # Summaries collection indexes
        await db.summaries.create_index([("user_id", 1), ("date", -1)])
        await db.summaries.create_index([("user_id", 1), ("type", 1)])
        
        print("Database indexes created successfully")
        
    except Exception as e:
        print(f"Error creating indexes: {e}")

async def save_analysis(db: motor.motor_asyncio.AsyncIOMotorDatabase, analysis_data: dict):
    """
    Save analysis result to database
    """
    try:
        result = await db.analyses.insert_one(analysis_data)
        return result.inserted_id
    except Exception as e:
        print(f"Error saving analysis: {e}")
        raise e

async def get_user_analyses(db: motor.motor_asyncio.AsyncIOMotorDatabase, user_id: str, limit: int = 30):
    """
    Get user's analysis history
    """
    try:
        cursor = db.analyses.find(
            {"user_id": user_id}
        ).sort("date", -1).limit(limit)
        
        analyses = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            analyses.append(doc)
        
        return analyses
    except Exception as e:
        print(f"Error fetching analyses: {e}")
        raise e

async def save_user_data(db: motor.motor_asyncio.AsyncIOMotorDatabase, user_data: dict):
    """
    Save or update user data
    """
    try:
        result = await db.users.update_one(
            {"user_id": user_data["user_id"]},
            {"$set": user_data},
            upsert=True
        )
        return result
    except Exception as e:
        print(f"Error saving user data: {e}")
        raise e

async def get_user_data(db: motor.motor_asyncio.AsyncIOMotorDatabase, user_id: str):
    """
    Get user data
    """
    try:
        user = await db.users.find_one({"user_id": user_id})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"Error fetching user data: {e}")
        raise e

async def save_summary(db: motor.motor_asyncio.AsyncIOMotorDatabase, summary_data: dict):
    """
    Save summary to database
    """
    try:
        result = await db.summaries.insert_one(summary_data)
        return result.inserted_id
    except Exception as e:
        print(f"Error saving summary: {e}")
        raise e

async def get_user_summaries(db: motor.motor_asyncio.AsyncIOMotorDatabase, user_id: str, summary_type: str = None, limit: int = 30):
    """
    Get user's summaries
    """
    try:
        query = {"user_id": user_id}
        if summary_type:
            query["type"] = summary_type
        
        cursor = db.summaries.find(query).sort("date", -1).limit(limit)
        
        summaries = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            summaries.append(doc)
        
        return summaries
    except Exception as e:
        print(f"Error fetching summaries: {e}")
        raise e
