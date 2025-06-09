from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# Import core modules
from core.logging import setup_logging, log_request_middleware

# Import route routers - uncomment as you create the FastAPI routers
from routes.auth import router as auth_router
# from routes.order_fastapi import router as order_router
# from routes.portfolio_fastapi import router as portfolio_router

# Initialize logging
logger = setup_logging(log_level='DEBUG')
logger.info("Starting DNSE Trading Bot API")

# Create the FastAPI application
app = FastAPI(
    title="DNSE Trading Bot API",
    description="API for trading operations with DNSE",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add logging middleware
app.middleware("http")(log_request_middleware)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }

# Include routers
app.include_router(auth_router, prefix='/api/dnse', tags=["Authentication"])
# app.include_router(market_router, prefix='/api/market', tags=["Market Data"])
# app.include_router(order_router, prefix='/api/order', tags=["Order Management"])
# app.include_router(portfolio_router, prefix='/api/portfolio', tags=["Portfolio"])

if __name__ == '__main__':
    # uvicorn is already imported at the top of the file
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
