from fastapi import APIRouter, HTTPException, status, Depends, Query
from bson import ObjectId

from app.modules.users.schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from app.modules.users.service import UserService
from app.core.dependencies import get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])
service = UserService()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def create_user(
    payload: UserCreate,
    _: str = Depends(get_current_admin),  # require admin
):
    """Create a new user (Admin only)"""
    try:
        return await service.create_user(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=UserListResponse,
    dependencies=[Depends(get_current_admin)],
)
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _: str = Depends(get_current_admin),  # require admin
):
    """Get all users (Admin only)"""
    return await service.get_all_users(skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin)],
)
async def get_user(
    user_id: str,
    _: str = Depends(get_current_admin),  # require admin
):
    """Get user by ID (Admin only)"""
    # Validate ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID",
        )

    user = await service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(get_current_admin)],
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    _: str = Depends(get_current_admin),  # require admin
):
    """Update user (PATCH) (Admin only)"""
    # Validate ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID",
        )

    try:
        user = await service.update_user(user_id, payload)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
async def delete_user(
    user_id: str,
    _: str = Depends(get_current_admin),  # require admin
):
    """Delete user - Soft delete (set status to inactive) (Admin only)"""
    # Validate ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID",
        )

    success = await service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
