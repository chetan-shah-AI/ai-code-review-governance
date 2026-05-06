from fastapi import APIRouter

router = APIRouter()



@router.get("/")
def health():
    return {"server": "running"}



@router.get("/health")
def health():
    return {"status": "ok"}
