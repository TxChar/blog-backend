"""
Script สำหรับสร้าง Admin account เริ่มต้น
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import hash_password


async def init_admin():
    # เชื่อมต่อ MongoDB
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db]

    # ตัวอย่าง admin account
    admin_username = "admin@example.com"
    admin_password = "Example@123"  # ⚠️ เปลี่ยนเป็น password ที่ปลอดภัยก่อนใช้งานจริง

    # เช็ค admin มีอยู่แล้วหรือไม่
    existing_admin = await db.users.find_one({
        "username": admin_username
    })

    if existing_admin:
        print(f"✓ Admin '{admin_username}' มีอยู่แล้ว")
        client.close()
        return

    # สร้าง admin account
    admin_doc = {
        "username": admin_username,
        "password_hash": hash_password(admin_password),
        "email": "admin@example.com",
        "is_admin": True,
        "is_active": True,
    }

    result = await db.users.insert_one(admin_doc)

    print(f"✓ สร้าง Admin account สำเร็จ")
    print(f"  Username: {admin_username}")
    print(f"  Email: admin@example.com")
    print(f"  ID: {result.inserted_id}")
    print("\n⚠️  อย่าลืมเปลี่ยน password ในไฟล์นี้เป็นค่าจริงก่อนใช้งาน")

    client.close()


if __name__ == "__main__":
    asyncio.run(init_admin())
