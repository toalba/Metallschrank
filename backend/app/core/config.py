from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Barcode providers (comma-separated, in fallback order)
    BARCODE_PROVIDERS: str = "openfoodfacts,opengtindb,upcitemdb"
    
    # CORS - parse from comma-separated string
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost"
    
    # Authentication (simple username/password for now)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def provider_list(self) -> List[str]:
        """Parse BARCODE_PROVIDERS into list"""
        return [p.strip() for p in self.BARCODE_PROVIDERS.split(",") if p.strip()]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into list"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
