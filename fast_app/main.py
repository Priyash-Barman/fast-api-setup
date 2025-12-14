from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config import APP_NAME, APP_VERSION
from fast_app.lifespan import lifespan
from fast_app.middlewares.exception_handler import ExceptionHandlerMiddleware
from fast_app.utils.register_routes import register_all_routes
from fast_app.modules import app_modules
from fast_app.utils.swagger import customize_swagger_ui

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/apidoc/v1",
    redoc_url="/redoc-ui",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Apply custom Swagger settings
customize_swagger_ui(app)

# Global Exception Handler Middleware
app.add_middleware(ExceptionHandlerMiddleware)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files globally
app.mount("/static", StaticFiles(directory="fast_app/static"), name="static")

# Register all routes
register_all_routes(app,app_modules)
