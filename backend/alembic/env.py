from logging.config import fileConfig
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models import Base
from dotenv import load_dotenv

# Determine environment
app_env = os.getenv("APP_ENV", "prod")
env_file = ".env.dev" if app_env == "dev" else ".env.prod"

# Load environment variables
if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file, override=True)
    print(f"Loaded environment from {env_file}")
else:
    print(f"Environment file {env_file} not found. Relying on injected environment variables.")

# Alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Build connection string from env
database_url = os.getenv("DATABASE_URL")
if not database_url:
    database_url = (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'postgres')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'postgres')}"
    )

config.set_main_option("sqlalchemy.url", database_url)
print("Alembic connecting to:", database_url)

# Metadata for migrations
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()