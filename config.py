import os

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///example.db")
    CLOUDFLARE_R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
    CLOUDFLARE_R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
    CLOUDFLARE_R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
    CLOUDFLARE_R2_BUCKET = os.getenv("R2_BUCKET_NAME")

