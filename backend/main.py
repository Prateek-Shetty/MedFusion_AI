from fastapi import FastAPI

from app.api.routes.ct import router as ct_router
from app.api.routes.modality import router as modality_router
from app.api.routes.mri import router as mri_router
from app.api.routes.model3a import router as model3a_router


app = FastAPI(
    title="MedFusion AI",
    version="1.0.0",
)


# Existing routes
app.include_router(ct_router)
app.include_router(modality_router)
app.include_router(mri_router)

# Model 3A
app.include_router(model3a_router)


@app.get("/")
def root():
    return {
        "message": "MedFusion AI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }