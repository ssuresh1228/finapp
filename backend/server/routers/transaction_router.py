from fastapi import APIRouter, Depends, Request, HTTPException, Form, Response
from server.dependencies import get_transaction_manager, get_user_manager
from server.schemas.transaction_schema import *
from server.util.user_manager import UserManager
from server.util.transaction_manager import TransactionManager
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.get("/transaction")
async def get_all_user_transactions(request: ReadTransactionValidator, transaction_manager: TransactionManager = Depends(get_transaction_manager), user_manager: UserManager = Depends(get_user_manager)):
    logger.debug(f"TransactionRouter Raw JSON data: {raw_data}")
    logger.debug(f"Received creation date: {transaction_request.creation_date}")
    transactions = await transaction_manager.get_user_transactions_by_user_id(request, user_manager)
    raw_data = await request.json()
    return transactions

@router.get("/transaction/date")
async def get_user_transcations_date_range(request: ReadTransactionDateRangeValidator, transaction_manager: TransactionManager = Depends(get_transaction_manager), user_manager: UserManager = Depends(get_user_manager)):
    transactions = await transaction_manager.get_transactions_by_date_range(request, user_manager)
    return transactions

@router.post("/transaction")
async def create_transaction(request: CreateTransactionValidator, transaction_manager: TransactionManager = Depends(get_transaction_manager), user_manager: UserManager = Depends(get_user_manager)):
    new_transaction = await transaction_manager.create_user_transaction(request, user_manager)
    return new_transaction 

@router.put("/transaction")
async def update_transaction(request: UpdateTransactionValidator, transaction_manager: TransactionManager = Depends(get_transaction_manager), user_manager: UserManager = Depends(get_user_manager)):
    updates = await transaction_manager.update_transactions_by_user(request, user_manager) 
    return updates
     
@router.delete("/transaction")
async def delete_transaction(request: DeleteTransactionValidator, transaction_manager: TransactionManager = Depends(get_transaction_manager), user_manager: UserManager = Depends(get_user_manager)):
    deleted_transactions = await transaction_manager.delete_transactions_by_user(request, user_manager)
    return deleted_transactions

@router.post("/test")
async def test_endpoint():
    logger.debug()