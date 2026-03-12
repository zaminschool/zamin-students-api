from fastapi import APIRouter
from routers.users import router as user_router
from routers.students import router as student_router

router = APIRouter(
    prefix="/api/v1",
)
router.include_router(user_router)
router.include_router(student_router)
