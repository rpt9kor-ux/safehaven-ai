from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.models.document import AccessLevel
from app.models.user import User, UserRole
from app.services.vector_store import search

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
def search_documents(
    q: str = Query(min_length=3, max_length=500),
    current_user: User = Depends(get_current_user),
):
    # The role decides which access levels may be searched
    if current_user.role == UserRole.HR_ADMIN.value:
        allowed = [AccessLevel.GENERAL.value, AccessLevel.HR_ONLY.value]
    else:
        allowed = [AccessLevel.GENERAL.value]

    return search(q, allowed, limit=5)