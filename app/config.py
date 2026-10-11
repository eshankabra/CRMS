import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "crms-fallback-secret-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "crms-fallback-jwt-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400")))
    
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    DB_NAME = os.getenv("DB_NAME", "crms_db")
    DB_POOL_NAME = "crms_pool"
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    
    MAX_CREDITS_PER_SEMESTER = int(os.getenv("MAX_CREDITS_PER_SEMESTER", "24"))
    
    # Swagger config
    SWAGGER = {
        "title": "CRMS - Course Registration & Management System API",
        "uiversion": 3,
        "version": "1.0.0",
        "description": "Backend REST API for Course Registration and Management System (VIT Vellore - Review 2)",
        "termsOfService": "",
        "specs_route": "/docs/",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        }
    }

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    DB_NAME = os.getenv("TEST_DB_NAME", "crms_test_db")
    DB_POOL_NAME = "crms_test_pool"

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
