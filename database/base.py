"""
Database connection and session management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class"""

    def __init__(self, db_url: str, pool_size: int = 5, max_overflow: int = 10):
        self.db_url = db_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    @classmethod
    def from_config(cls, config_module):
        """Create from config module"""
        return cls(
            db_url=config_module.DB_URL,
            pool_size=config_module.DB_POOL_SIZE,
            max_overflow=config_module.DB_MAX_OVERFLOW
        )


class DatabaseManager:
    """Database connection manager"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """Create database engine and session factory"""
        try:
            self.engine = create_engine(
                self.config.db_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True,  # Verify connections before using
                echo=False,  # Set to True for SQL query logging
                future=True  # Use SQLAlchemy 2.0 style
            )

            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                future=True
            )

            logger.info(f"Database engine created successfully: {self.config.db_url.split('@')[1] if '@' in self.config.db_url else 'local'}")
            return True

        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            return False

    def disconnect(self):
        """Dispose of the engine and close all connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def create_tables(self, base):
        """Create all tables in the database"""
        try:
            base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            return False

    def drop_tables(self, base):
        """Drop all tables (USE WITH CAUTION)"""
        try:
            base.metadata.drop_all(bind=self.engine)
            logger.warning("Database tables dropped")
            return True
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            return False

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database manager instance
_db_manager: DatabaseManager = None


def init_database(config_module) -> DatabaseManager:
    """Initialize the global database manager"""
    global _db_manager

    if not config_module.DB_ENABLED:
        logger.info("Database is disabled in configuration")
        return None

    db_config = DatabaseConfig.from_config(config_module)
    _db_manager = DatabaseManager(db_config)

    if _db_manager.connect():
        return _db_manager
    else:
        logger.error("Failed to initialize database manager")
        return None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return _db_manager


@contextmanager
def get_db_session():
    """Get a database session from the global manager"""
    if _db_manager is None:
        raise RuntimeError("Database manager not initialized")

    with _db_manager.get_session() as session:
        yield session


def is_database_enabled() -> bool:
    """Check if database is enabled and initialized"""
    return _db_manager is not None
