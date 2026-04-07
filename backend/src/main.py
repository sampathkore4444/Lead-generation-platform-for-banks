"""
Main Entry Point
Run the application with uvicorn
"""

import uvicorn
from .config.settings import settings
from .core.fastapi import app


if __name__ == "__main__":
    uvicorn.run(
        "src.core.fastapi:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
