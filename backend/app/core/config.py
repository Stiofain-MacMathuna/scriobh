import os
from dotenv import load_dotenv

dotenv_file = os.getenv("DOTENV", ".env")
load_dotenv(dotenv_file, override=True)

#JWT
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-override")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Database
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "disable")
DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", "1"))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", "10"))
DB_POOL_MODE = os.getenv("DB_POOL_MODE", "session")
DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "10"))