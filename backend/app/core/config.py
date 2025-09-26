import os
from dotenv import load_dotenv

# Determine environment
app_env = os.getenv("APP_ENV", "prod")

# Choose env file based on environment
env_file = ".env.dev" if app_env == "dev" else ".env.prod"
print("Loading env file:", env_file)

# Load it if it exists
if os.path.exists(env_file):
    load_dotenv(env_file, override=True)
    print("DB_HOST from env:", os.getenv("DB_HOST"))
else:
    print("Env file not found:", env_file)

# JWT
def get_jwt_secret():
    return os.getenv("JWT_SECRET", "dev-only-override")

def get_jwt_alg():
    return os.getenv("JWT_ALG", "HS256")

def get_access_token_expiry():
    return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Database
def get_db_user():
    return os.getenv("DB_USER", "postgres")

def get_db_password():
    return os.getenv("DB_PASSWORD", "postgres")

def get_db_host():
    return os.getenv("DB_HOST", "localhost")

def get_db_port():
    return os.getenv("DB_PORT", "5432")

def get_db_name():
    return os.getenv("DB_NAME", "postgres")

def get_db_ssl_mode():
    return os.getenv("DB_SSL_MODE", "disable")

def get_db_pool_min():
    return int(os.getenv("DB_POOL_MIN", "1"))

def get_db_pool_max():
    return int(os.getenv("DB_POOL_MAX", "10"))

def get_db_pool_mode():
    return os.getenv("DB_POOL_MODE", "session")

def get_db_timeout():
    return int(os.getenv("DB_TIMEOUT", "10"))