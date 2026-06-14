"""
数据库迁移脚本 - 添加 detections 列
"""
import sqlite3
from pathlib import Path
from config import settings

def migrate_database():
    """添加 detections 列到 detection_records 表"""
    db_path = settings.DB_PATH
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 检查 detections 列是否已存在
        cursor.execute("PRAGMA table_info(detection_records)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'detections' in columns:
            print("✅ detections 列已存在，无需迁移")
            return True
        
        # 添加 detections 列
        print("正在添加 detections 列...")
        cursor.execute("ALTER TABLE detection_records ADD COLUMN detections TEXT")
        conn.commit()
        print("✅ 成功添加 detections 列")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("数据库迁移脚本")
    print("=" * 50)
    success = migrate_database()
    if success:
        print("\n✅ 迁移完成！")
    else:
        print("\n❌ 迁移失败！")
