# from app.models.user import User
# from sqlalchemy import select
# from fastapi import Depends, APIRouter
# from typing import Annotated
# from sqlalchemy.exc import IntegrityError
# from app.backend.db_depends import get_db, AsyncSession
#
# router = APIRouter(prefix='/delete', tags=['delete'])
#
# @router.delete('/{id_user}')
# async def delete_user(db: Annotated[AsyncSession, Depends(get_db)], id_user: int):
#     res = await db.scalar(select(User).where(User.id == id_user))
#     await db.delete(res)
#     await db.commit()
#     return {
#         'status': 'Successful'
#     }