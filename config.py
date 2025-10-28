import os

class Config:
    DATABASE_URL = 'postgresql://lessons_db_7sii_user:RJZXEo09gpLpSru362xc8lotOEMHYbjd@dpg-d40l6o7diees73d8gaa0-a.oregon-postgres.render.com/lessons_db_7sii'
    CLOUDFLARE_R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
    CLOUDFLARE_R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
    CLOUDFLARE_R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
    CLOUDFLARE_R2_BUCKET = os.getenv("R2_BUCKET_NAME")


