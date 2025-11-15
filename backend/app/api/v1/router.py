from fastapi import APIRouter
from app.api.v1.endpoints import auth, finance, documents, marketing, tasks, chat, search

api_router = APIRouter()

# Include auth router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include finance router
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])

# Include documents router
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# Include marketing router
api_router.include_router(marketing.router, prefix="/marketing", tags=["marketing"])

# Include tasks router
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

# Include chat router
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Include search router
api_router.include_router(search.router, prefix="/search", tags=["search"])

@api_router.get("/")
async def api_root():
    return {"message": "API v1 is running"}

