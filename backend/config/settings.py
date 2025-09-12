"""
Application settings and configuration management.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str = "sqlite:///countrycompare.db"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    echo_pool: bool = False


@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str = "redis://localhost:6379/0"
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5


@dataclass
class APIConfig:
    """External API configuration."""
    rest_countries_base_url: str = "https://restcountries.com/v3.1"
    world_bank_base_url: str = "https://api.worldbank.org/v2"
    timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour


@dataclass
class CacheConfig:
    """Cache configuration."""
    default_ttl: int = 3600  # 1 hour
    max_size: int = 1000
    cleanup_interval: int = 300  # 5 minutes
    enable_compression: bool = True
    compression_level: int = 6


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration_delta: int = 3600  # 1 hour
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    cors_headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    console_output: bool = True
    file_output: bool = False


@dataclass
class AWSSettings:
    """AWS configuration."""
    region: str = "us-east-1"
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    cloudfront_distribution_id: Optional[str] = None
    rds_endpoint: Optional[str] = None
    rds_port: int = 5432
    rds_database_name: str = "countrycompare"
    rds_username: str = "postgres"
    rds_password: Optional[str] = None


@dataclass
class ApplicationSettings:
    """Main application settings."""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5001
    workers: int = 4
    app_name: str = "CountryCompare"
    version: str = "1.0.0"
    description: str = "Country comparison API with interactive charts"
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    api: APIConfig = field(default_factory=APIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    aws: AWSSettings = field(default_factory=AWSSettings)


class SettingsManager:
    """Settings manager for loading and managing configuration."""
    
    def __init__(self):
        self.settings: Optional[ApplicationSettings] = None
        self._load_settings()
    
    def _load_settings(self) -> None:
        """Load settings from environment variables and config files."""
        # Load from environment variables
        env_settings = self._load_from_environment()
        
        # Load from config file if exists
        config_file = os.getenv('CONFIG_FILE', 'config.json')
        file_settings = self._load_from_file(config_file)
        
        # Merge settings (environment takes precedence)
        merged_settings = self._merge_settings(file_settings, env_settings)
        
        # Create settings object
        self.settings = self._create_settings_object(merged_settings)
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load settings from environment variables."""
        env_settings = {}
        
        # Application settings
        if os.getenv('FLASK_ENV'):
            env_settings['environment'] = os.getenv('FLASK_ENV')
        if os.getenv('FLASK_DEBUG'):
            env_settings['debug'] = os.getenv('FLASK_DEBUG').lower() == 'true'
        if os.getenv('HOST'):
            env_settings['host'] = os.getenv('HOST')
        if os.getenv('PORT'):
            env_settings['port'] = int(os.getenv('PORT'))
        if os.getenv('WORKERS'):
            env_settings['workers'] = int(os.getenv('WORKERS'))
        
        # Database settings
        if os.getenv('DATABASE_URL'):
            env_settings['database'] = {'url': os.getenv('DATABASE_URL')}
        
        # Redis settings
        if os.getenv('REDIS_URL'):
            env_settings['redis'] = {'url': os.getenv('REDIS_URL')}
        
        # Security settings
        if os.getenv('SECRET_KEY'):
            env_settings['security'] = {'secret_key': os.getenv('SECRET_KEY')}
        
        # AWS settings
        aws_settings = {}
        if os.getenv('AWS_REGION'):
            aws_settings['region'] = os.getenv('AWS_REGION')
        if os.getenv('AWS_ACCESS_KEY_ID'):
            aws_settings['access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
        if os.getenv('AWS_SECRET_ACCESS_KEY'):
            aws_settings['secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
        if os.getenv('S3_BUCKET_NAME'):
            aws_settings['s3_bucket_name'] = os.getenv('S3_BUCKET_NAME')
        if aws_settings:
            env_settings['aws'] = aws_settings
        
        # Logging settings
        if os.getenv('LOG_LEVEL'):
            env_settings['logging'] = {'level': os.getenv('LOG_LEVEL')}
        if os.getenv('LOG_FILE'):
            env_settings['logging'] = env_settings.get('logging', {})
            env_settings['logging']['file_path'] = os.getenv('LOG_FILE')
        
        return env_settings
    
    def _load_from_file(self, config_file: str) -> Dict[str, Any]:
        """Load settings from JSON configuration file."""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Could not load config file {config_file}: {e}")
        
        return {}
    
    def _merge_settings(self, file_settings: Dict[str, Any], env_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge file and environment settings."""
        merged = file_settings.copy()
        
        def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
            """Deep update dictionary."""
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(merged, env_settings)
        return merged
    
    def _create_settings_object(self, settings_dict: Dict[str, Any]) -> ApplicationSettings:
        """Create ApplicationSettings object from dictionary."""
        # Create sub-configuration objects
        database_config = DatabaseConfig(**settings_dict.get('database', {}))
        redis_config = RedisConfig(**settings_dict.get('redis', {}))
        api_config = APIConfig(**settings_dict.get('api', {}))
        cache_config = CacheConfig(**settings_dict.get('cache', {}))
        security_config = SecurityConfig(**settings_dict.get('security', {}))
        logging_config = LoggingConfig(**settings_dict.get('logging', {}))
        aws_config = AWSSettings(**settings_dict.get('aws', {}))
        
        # Create main settings object
        main_settings = {
            'environment': Environment(settings_dict.get('environment', 'development')),
            'debug': settings_dict.get('debug', False),
            'host': settings_dict.get('host', '0.0.0.0'),
            'port': settings_dict.get('port', 5001),
            'workers': settings_dict.get('workers', 4),
            'app_name': settings_dict.get('app_name', 'CountryCompare'),
            'version': settings_dict.get('version', '1.0.0'),
            'description': settings_dict.get('description', 'Country comparison API with interactive charts'),
            'database': database_config,
            'redis': redis_config,
            'api': api_config,
            'cache': cache_config,
            'security': security_config,
            'logging': logging_config,
            'aws': aws_config
        }
        
        return ApplicationSettings(**main_settings)
    
    def get_settings(self) -> ApplicationSettings:
        """Get current settings."""
        if self.settings is None:
            self._load_settings()
        return self.settings
    
    def reload_settings(self) -> None:
        """Reload settings from sources."""
        self._load_settings()
    
    def validate_settings(self) -> List[str]:
        """Validate current settings and return list of issues."""
        issues = []
        
        if not self.settings:
            issues.append("Settings not loaded")
            return issues
        
        # Validate database URL
        if not self.settings.database.url:
            issues.append("Database URL is required")
        
        # Validate secret key in production
        if (self.settings.environment == Environment.PRODUCTION and 
            self.settings.security.secret_key == "dev-secret-key-change-in-production"):
            issues.append("Secret key must be changed in production")
        
        # Validate AWS settings if provided
        if self.settings.aws.access_key_id and not self.settings.aws.secret_access_key:
            issues.append("AWS secret access key is required if access key ID is provided")
        
        # Validate logging file path
        if (self.settings.logging.file_output and 
            self.settings.logging.file_path and 
            not Path(self.settings.logging.file_path).parent.exists()):
            issues.append(f"Log file directory does not exist: {self.settings.logging.file_path}")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        if not self.settings:
            return {}
        
        return {
            'environment': self.settings.environment.value,
            'debug': self.settings.debug,
            'host': self.settings.host,
            'port': self.settings.port,
            'workers': self.settings.workers,
            'app_name': self.settings.app_name,
            'version': self.settings.version,
            'description': self.settings.description,
            'database': {
                'url': self.settings.database.url,
                'pool_size': self.settings.database.pool_size,
                'max_overflow': self.settings.database.max_overflow,
                'pool_timeout': self.settings.database.pool_timeout,
                'pool_recycle': self.settings.database.pool_recycle,
                'echo': self.settings.database.echo,
                'echo_pool': self.settings.database.echo_pool
            },
            'redis': {
                'url': self.settings.redis.url,
                'host': self.settings.redis.host,
                'port': self.settings.redis.port,
                'db': self.settings.redis.db,
                'max_connections': self.settings.redis.max_connections,
                'socket_timeout': self.settings.redis.socket_timeout,
                'socket_connect_timeout': self.settings.redis.socket_connect_timeout
            },
            'api': {
                'rest_countries_base_url': self.settings.api.rest_countries_base_url,
                'world_bank_base_url': self.settings.api.world_bank_base_url,
                'timeout': self.settings.api.timeout,
                'max_retries': self.settings.api.max_retries,
                'retry_delay': self.settings.api.retry_delay,
                'rate_limit_requests': self.settings.api.rate_limit_requests,
                'rate_limit_window': self.settings.api.rate_limit_window
            },
            'cache': {
                'default_ttl': self.settings.cache.default_ttl,
                'max_size': self.settings.cache.max_size,
                'cleanup_interval': self.settings.cache.cleanup_interval,
                'enable_compression': self.settings.cache.enable_compression,
                'compression_level': self.settings.cache.compression_level
            },
            'security': {
                'jwt_algorithm': self.settings.security.jwt_algorithm,
                'jwt_expiration_delta': self.settings.security.jwt_expiration_delta,
                'password_min_length': self.settings.security.password_min_length,
                'max_login_attempts': self.settings.security.max_login_attempts,
                'lockout_duration': self.settings.security.lockout_duration,
                'cors_origins': self.settings.security.cors_origins,
                'cors_methods': self.settings.security.cors_methods,
                'cors_headers': self.settings.security.cors_headers
            },
            'logging': {
                'level': self.settings.logging.level.value,
                'format': self.settings.logging.format,
                'date_format': self.settings.logging.date_format,
                'file_path': self.settings.logging.file_path,
                'max_file_size': self.settings.logging.max_file_size,
                'backup_count': self.settings.logging.backup_count,
                'console_output': self.settings.logging.console_output,
                'file_output': self.settings.logging.file_output
            },
            'aws': {
                'region': self.settings.aws.region,
                's3_bucket_name': self.settings.aws.s3_bucket_name,
                'cloudfront_distribution_id': self.settings.aws.cloudfront_distribution_id,
                'rds_endpoint': self.settings.aws.rds_endpoint,
                'rds_port': self.settings.aws.rds_port,
                'rds_database_name': self.settings.aws.rds_database_name,
                'rds_username': self.settings.aws.rds_username
            }
        }


# Global settings manager instance
settings_manager = SettingsManager()


def get_settings() -> ApplicationSettings:
    """Get application settings."""
    return settings_manager.get_settings()


def reload_settings() -> None:
    """Reload application settings."""
    settings_manager.reload_settings()


def validate_settings() -> List[str]:
    """Validate application settings."""
    return settings_manager.validate_settings()
