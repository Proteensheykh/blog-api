"""Configuration settings for the application.

This module defines the application's configuration settings using Pydantic's BaseSettings.
It handles loading and validating configuration from environment variables and .env files.

All settings are required and must be provided either through environment
variables or a .env file. Settings are automatically parsed and validated
when the application starts.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        """Pydantic configuration for settings.
        
        Specifies the .env file to load environment variables from.
        """
        env_file = ".env"

settings = Settings()
