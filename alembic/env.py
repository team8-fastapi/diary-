import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logging.config import fileConfig
from app.models import user
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.database import Base  # Base.metadata 사용


# Alembic Config 객체
config = context.config

# ✅ DB URL 동적 주입 (이걸 가장 먼저!)
db_url = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASS', 'rootpassword')}@{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'octo')}"

config.set_main_option("sqlalchemy.url", db_url)

# Logging 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ 마이그레이션 대상 메타데이터
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
