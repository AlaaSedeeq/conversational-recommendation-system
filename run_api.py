import uvicorn
from src.common.config import load_config

CONFIG = load_config()

if __name__ == "__main__":
    uvicorn.run(
        "src.presentation.api.main:app",
        host="0.0.0.0",
        port=CONFIG.api.port,
        workers=4,
        reload=True 
    )