"""
Creates the first admin user. Run with:
python -m scripts.create_admin admin@example.com yourpassword
"""
import sys

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import AdminUser

if len(sys.argv) != 3:
    print("Usage: python -m scripts.create_admin <email> <password>")
    sys.exit(1)

email, password = sys.argv[1], sys.argv[2]

db = SessionLocal()
if db.query(AdminUser).filter(AdminUser.email == email).first():
    print(f"Admin '{email}' already exists.")
else:
    admin = AdminUser(email=email, password_hash=hash_password(password))
    db.add(admin)
    db.commit()
    print(f"Admin user '{email}' created.")
db.close()
