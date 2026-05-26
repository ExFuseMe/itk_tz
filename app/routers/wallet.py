from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.models import Wallet
from app.schemas.wallet import OperationType, WalletOut, WalletUpdate

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


async def _get_wallet(db: AsyncSession, wallet_uuid: str):
    return await db.get(Wallet, wallet_uuid)


async def _get_wallet_for_update(db: AsyncSession, wallet_uuid: str):
    result = await db.execute(
        select(Wallet).where(Wallet.uuid == wallet_uuid).with_for_update()
    )
    return result.scalar_one_or_none()


@router.get("/{wallet_uuid}", response_model=WalletOut)
async def get_wallet(wallet_uuid: str, db: AsyncSession = Depends(get_db)):
    wallet = await _get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.post("/{wallet_uuid}/operation", response_model=WalletOut)
async def create_or_update_wallet(
    wallet_uuid: str,
    payload: WalletUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_wallet = await _get_wallet_for_update(db, wallet_uuid=wallet_uuid)

    if payload.amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Нельзя указывать отрицательные значения",
        )
    if not db_wallet:
        if payload.operation_type == OperationType.WITHDRAW:
            raise HTTPException(status_code=400, detail="Недостаточно средств")
        db_wallet = Wallet(uuid=wallet_uuid, balance=payload.amount)
    else:
        if payload.operation_type == OperationType.DEPOSIT:
            db_wallet.balance += payload.amount
        elif payload.operation_type == OperationType.WITHDRAW:
            if db_wallet.balance < payload.amount:
                raise HTTPException(
                    status_code=400, detail="Недостаточно средств"
                )
            db_wallet.balance -= payload.amount

    db.add(db_wallet)
    await db.commit()
    await db.refresh(db_wallet)

    return db_wallet
