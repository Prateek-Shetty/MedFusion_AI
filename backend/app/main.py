from fastapi import FastAPI

from app.api.routes.ct import router as ct_router
from app.api.routes.modality import router as modality_router
from app.api.routes.mri import router as mri_router
from app.api.routes.model3 import router as model3_router
from app.api.routes.model4 import router as model4_router
from app.api.routes.model5 import router as model5_router
from app.api.routes.analysis import router as analysis_router


app = FastAPI(
    title="MedFusion AI",
    version="1.0.0",
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(ct_router)
app.include_router(modality_router)
app.include_router(mri_router)
app.include_router(model3_router)
app.include_router(model4_router)
app.include_router(model5_router)
app.include_router(analysis_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "MedFusion AI API is running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }
