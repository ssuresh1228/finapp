from decimal import Decimal
from typing import Any
from bson import Decimal128 as _Decimal128
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

# enables use of a "unified" decimal format between backend and mongo
class PyDecimal128(_Decimal128):
    
    # how pydantic builds the core schema for PyDecimal128 type
    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[Any], handler:GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema( 
            python_schema=core_schema.with_info_plain_validator_function(cls.__validate),      # how to validate inputs with cls._validate: e.g. converting from string -> PyDecimal128
            json_schema=core_schema.decimal_schema(gt=0.0, max_digits = 2, decimal_places=2),  # how this schema is represented in JSON: must be > 0.00
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: str(instance)), # serialize PyDecimal128 instances as strings in JSON 
        )
        
    # json serialization definition: takes CoreSchema object and json schema handler to process the schema
    @classmethod
    def __get_pydantic_json_schema__(cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(schema)   # pydantic handler called on current schema to return JsonSchemaValue - pydantic's representation of json schenmas 
        json_schema.update(             # updates json schema with PyDecimal128's details - sets type to Decimal128 and gives an example so clients know what to treat this as 
            type="Decimal128",
            example = "12.34",
        )
        return json_schema
    
    # define how pydantic should handle validation
    @classmethod
    def __validate(cls, v, _:core_schema.ValidationInfo):
        # checks in incoming value v is already an instance of mongo Decimal128 and returns it if (no validation needed to save in db)
        if isinstance(v, _Decimal128):
            return v
        return cls(Decimal(v))  # wraps incoming value to python Decimal, then wraps that with Decimal128 so it's stored in db with valid type