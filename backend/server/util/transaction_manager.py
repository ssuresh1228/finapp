from server.model.transaction_model import Category, Transaction
from server.schemas.transaction_schema import *
from beanie import PydanticObjectId
from server.model.user_model import User
from bson import ObjectId, Decimal128
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi import Depends, HTTPException
from loguru import logger

class TransactionManager:
    
    # creates a single new transaction
    @logger.catch
    async def create_user_transaction(self, transaction_request: CreateTransactionValidator, user_manager):
        # Validate and get the user
        user = await user_manager.get_user_by_id(transaction_request.userID)
        if not user:
            raise ValueError("User not found")

        # Convert categories to Category model instances
        category_models = [Category(name=cat.name, description=cat.description) 
                           for cat in transaction_request.categories]
        
        # Create a new Transaction instance
        new_transaction = Transaction(
            userID=transaction_request.userID,
            amount=transaction_request.amount,
            creation_date=transaction_request.creation_date,
            categories=category_models
        )

        # Save the new transaction
        await new_transaction.save()
        return {"message": "Transaction successfully saved"}
    
    # returns all transactions (5 at a time) associated with a userID sorted by descending date        
    async def get_user_transactions_by_user_id(self, get_transaction_request: ReadTransactionValidator, user_manager):
        try:
            # validate and get the user 
            user = await user_manager.get_user_by_id(get_transaction_request.userID)
            
            # calculate offset for pagination 
            amount_to_skip = (get_transaction_request.page - 1) * get_transaction_request.page_size
            
            # fetch list of sorted transactions with limit and skip as a list
            user_transactions = await Transaction.find(Transaction.userID == user.id).sort("-date").limit(get_transaction_request.page_size).to_list()
            
            # raise error if user is valid but has no transactions left to load
            if not user_transactions:
                raise ValueError("Error - no more transactions available")
            return user_transactions
        except ValueError as e:
            raise HTTPException(status_code=404, detail="Error - no transactions were recorded to retrieve")
        except ValidationErr as e:
            raise HTTPException(status_code=500, detail="Data failed validation")
            
    # returns all transactions (5 at a time) associated with userID and specified category sorted by descending date
    async def get_user_transactions_by_category(self, get_transaction_request: ReadTransactionValidator, user_manager):
        try:

            # validate and get the user 
            user = await user_manager.get_user_by_id(get_transaction_request.userID)
            
            # get the specified categories
            request_categories = get_transaction_request.categories
            
            # calculate offset for pagination 
            amount_to_skip = (get_transaction_request.page - 1) * get_transaction_request.page_size
            
            # fetch list of sorted transactions with limit and skip as a list
            user_transactions = await Transaction.find(
                Transaction.userID == user.id &
                Transaction.categories.any_in(request_categories)).sort("-date").limit(get_transaction_request.page_size).to_list()
            
            # raise error if user is valid but has no transactions left to load
            if not user_transactions:
                raise ValueError("Error - no more transactions available")
            return user_transactions
        except ValueError as e:
            raise HTTPException(status_code=404, detail="Error - no transactions were recorded to retrieve")
        except ValidationError as e:
            raise HTTPException(status_code=500, detail="Data failed validation")
        
    # returns transactions made on a specified date
    async def get_transactions_by_date(self, get_transaction_request: ReadTransactionValidator, user_manager):
        try:
            # validate and get the user

            user = await user_manager.get_user_by_id(get_transaction_request.userID)
            
            # get the transactions made on specified date
            request_date = get_transaction_request.creation_date
            
            # calculate offset for pagination 
            amount_to_skip = (get_transaction_request.page - 1) * get_transaction_request.page_size
            
            # fetch list of sorted transactions with limit and skip as a list
            user_transactions = await Transaction.find(
                Transaction.userID == user.id &
                Transaction.creation_date.any_in(request_date)).limit(get_transaction_request.page_size).to_list()
            
            # raise error if user is valid but has no transactions left to load
            if not user_transactions:
                raise ValueError("Error - no more transactions available")
            return user_transactions
        except ValueError as e:
            raise HTTPException(status_code=404, detail="Error - no transactions were recorded to retrieve")
        except ValidationError as e:
            raise HTTPException(status_code=500, detail="Data failed to be validated")
    
    # returns transactions made in specified date range
    async def get_transactions_by_date_range(self, get_transaction_request: ReadTransactionDateRangeValidator, user_manager):
        try:
            # validate and get the user

            user = await user_manager.get_user_by_id(get_transaction_request.userID)
            
            # get specified start/end dates
            request_start_date = get_transaction_request.start_date
            request_end_date = get_transaction_request.end_date

            # calculate offset for pagination 
            amount_to_skip = (get_transaction_request.page - 1) * get_transaction_request.page_size
            
            # fetch list of sorted transactions with limit and skip as a list
            user_transactions = await Transaction.find(
                Transaction.userID == user.id &
                Transaction.creation_date >= get_transaction_request.start_date &
                Transaction.creation_date <= get_transaction_request.end_date
            )
            # raise error if user is valid but has no transactions left to load
            if not user_transactions:
                raise ValueError("Error - no more transactions available")
            return user_transactions
        except ValueError as e:
            raise HTTPException(status_code=404, detail="Error - no transactions were recorded to retrieve")
        except ValidationError as e:
            raise HTTPException(status_code=500, detail="Data failed to be validated")
     
    # deletes specified transactions
    async def delete_transactions_by_user(self, delete_transaction_request: DeleteTransactionValidator, user_manager):
         try:
             user = await user_manager.get_user_by_id(delete_transaction_request.userID)
            
             # delete the specified transactions by user ID
             delete_result = await Transaction.delete_many(
                 (Transaction.id.in_(delete_transaction_request.transaction_ids)) &
                 (Transaction.userID == user.id)
             )
             if delete_result == 0:
                 raise ValueError("Error - no transactions were deleted")
             return {"message": "{delete_result.deleted_count} transactions were successfully deleted"}
         except ValueError as e:
             raise HTTPException(status_code=404, detail=str(e))
         except ValidationError as e:
             raise HTTPException(status_code=500, detail=str(e))
         
    # updates field(s) of 1 transaction
    async def update_transactions_by_user(self, update_transaction_request: BulkUpdateTransactionUpdateRequest, user_manager):
        transactions_updated: [] 
        # get and validate the user
        user = await user_manager.get_user_by_id(update_transaction_request.userID)
            
        for update_selection in update_transaction_request.update_selection:
            # get IDs of transactions and verify against user's ID
            transaction = await Transaction.get(update_selection.id)
            if not transaction or transaction.userID != user.id:
                raise HTTPException(status_code=400, detail=f"Transaction not found: {update.transaction_id}")
                
            # update fields if given 
            if transaction_to_update.amount is not None:
                transaction.amount = update_selection.amount
            if transaction_to_update.pydate is not None:
                transaction.pydate = update_selection.pydate
            if transaction_to_update.categories is not None:
                transaction.categories = update_selection.categories
                    
                # save updated fields and append updated transactions to the list 
                await transaction.save()
                transactions_updated.append(transaction)
        return transactions_updated, {"message": f"{transactions_updated.count} transactions updated"}