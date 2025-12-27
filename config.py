import os
from dotenv import load_dotenv

load_dotenv()

# Load the environment (e.g., loc, dev, prod, test, uat)
ENV: str = os.getenv("ENV", "dev").lower()

# Define a prefix based on the environment
ENV_PREFIX = ENV.upper()  # e.g., 'LOC', 'DEV', 'PROD', 'TEST', 'UAT'

# Helper to fetch environment-specific values
def get_env_var(key: str, default=None):
    return os.getenv(f"{ENV_PREFIX}_{key}", default)

# common variables
APP_NAME: str = os.getenv("APP_NAME", 'APP')
APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
PORT: int = int(os.getenv("PORT", 8000))
RELOAD: bool = os.getenv("RELOAD", "true").lower() in ("true", "1", "yes")
EMAIL_ID: str = os.getenv("MAIL_USERNAME", "")
EMAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
JWT_ACCESS_SECRET_KEY: str = os.getenv("JWT_ACCESS_SECRET_KEY","")
JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY","")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 2))

BUCKET: str = os.getenv("BUCKET", "local")
AWS_S3_BUCKET_NAME: str = os.getenv("AWS_S3_BUCKET_NAME", "")
AWS_S3_BUCKET_USER: str = os.getenv("AWS_S3_BUCKET_USER", "")
AWS_S3_BUCKET_REGION: str = os.getenv("AWS_S3_BUCKET_REGION", "")
AWS_S3_BUCKET_ACCESS_KEY: str = os.getenv("AWS_S3_BUCKET_ACCESS_KEY", "")
AWS_S3_BUCKET_SECRET_KEY: str = os.getenv("AWS_S3_BUCKET_SECRET_KEY", "")
AWS_S3_BUCKET_HOST: str = os.getenv("AWS_S3_BUCKET_HOST", "")

# Use environment-specific variables
MONGO_URI: str = get_env_var("MONGO_URI") or ""
DB_NAME: str = get_env_var("DB_NAME") or ""
FIREBASE_PROJECT_ID: str = get_env_var("FIREBASE_PROJECT_ID") or ""
FIREBASE_CLIENT_EMAIL: str = get_env_var("FIREBASE_CLIENT_EMAIL") or ""
FIREBASE_PRIVATE_KEY: str = get_env_var("FIREBASE_PRIVATE_KEY") or ""
