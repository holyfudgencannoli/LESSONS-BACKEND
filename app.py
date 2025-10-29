from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import boto3
from werkzeug.utils import secure_filename
import os
import uuid

# --- Flask app setup ---
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": ["https://awesome-guitar-lessons.pages.dev"]}}, supports_credentials=True)

# --- Validate environment ---
for key in [
    "CLOUDFLARE_R2_ACCOUNT_ID",
    "CLOUDFLARE_R2_ACCESS_KEY_ID",
    "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
    "CLOUDFLARE_R2_BUCKET",
]:
    if not app.config.get(key):
        raise RuntimeError(f"Missing required config: {key}")

# --- SQLAlchemy setup ---
Base = declarative_base()
engine = create_engine(app.config["DATABASE_URL"], echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# --- Cloudflare R2 client ---
r2 = boto3.client(
    "s3",
    endpoint_url=f"https://{app.config['CLOUDFLARE_R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=app.config["CLOUDFLARE_R2_ACCESS_KEY_ID"],
    aws_secret_access_key=app.config["CLOUDFLARE_R2_SECRET_ACCESS_KEY"],
)

# --- Database Model ---
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    license_number = Column(String)
    license_image_url = Column(String)
    created_at = Column(String)
    accepted_policy = Column(Boolean)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "license_number": self.license_number,
            "license_image_url": self.license_image_url,
        }

Base.metadata.create_all(bind=engine)

# --- Routes ---
@app.route("/api/lessons", methods=["OPTIONS"])
def options_lessons():
    return jsonify({"ok": True}), 200

@app.route("/api/lessons", methods=["POST"])
def register_lesson():
    db_session = SessionLocal()
    try:
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        address = request.form.get("address")
        license_number = request.form.get("licenseNumber")
        license_file = request.files.get("licenseImage")

        if not license_file:
            return jsonify({"error": "License image is required"}), 400

        filename = secure_filename(license_file.filename)
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"

        # Upload to Cloudflare R2
        r2.upload_fileobj(
            license_file,
            app.config["CLOUDFLARE_R2_BUCKET"],
            unique_name,
            ExtraArgs={"ContentType": license_file.mimetype},
        )

        file_url = (
            f"https://{app.config['CLOUDFLARE_R2_ACCOUNT_ID']}.r2.cloudflarestorage.com/"
            f"{app.config['CLOUDFLARE_R2_BUCKET']}/{unique_name}"
        )

        new_student = Student(
            name=name,
            phone=phone,
            email=email,
            address=address,
            license_number=license_number,
            license_image_url=file_url,
            created_at=datetime.utcnow().isoformat(),
            accepted_policy=True,
        )

        db_session.add(new_student)
        db_session.commit()

        return jsonify({"message": "Lesson request submitted successfully", "file_url": file_url}), 201

    except Exception as e:
        print("Error:", e)
        db_session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db_session.close()

if __name__ == "__main__":
    app.run(debug=True)


