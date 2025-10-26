#!/usr/bin/env python3
"""
Debug script to test model imports and relationships
"""
import sys
import os

def test_imports():
    print("🧪 Testing model imports...")
    
    try:
        print("1. Importing database...")
        from app.db.database import Base, engine
        print("✅ Database imported")
        
        print("2. Importing User model...")
        from app.models.user import User
        print("✅ User model imported")
        
        print("3. Importing DailyHabitEntry model...")
        from app.models.habit_entry import DailyHabitEntry
        print("✅ DailyHabitEntry model imported")
        
        print("4. Testing relationships...")
        print(f"   User.daily_habit_entries: {hasattr(User, 'daily_habit_entries')}")
        print(f"   DailyHabitEntry.user: {hasattr(DailyHabitEntry, 'user')}")
        
        print("5. Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
