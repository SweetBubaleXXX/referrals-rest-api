from uuid import UUID

from fastapi import APIRouter, status

router = APIRouter(tags=["referrals"])


@router.get("/codes")
async def list_codes(): ...


@router.post("/codes")
async def create_code(): ...


@router.delete("/codes/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_code(code_id: UUID) -> None: ...


@router.get("/codes/{code_id}/referees")
async def list_referees(code_id: UUID): ...


@router.post("/codes/{code_id}/referees")
async def register_using_code(code_id: UUID): ...
