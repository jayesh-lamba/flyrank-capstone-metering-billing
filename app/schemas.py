from pydantic import BaseModel, Field
class TenantIn(BaseModel):
    id:str=Field(min_length=1,max_length=80)
    name:str=Field(min_length=1,max_length=160)
class UsageIn(BaseModel):
    tenant_id:str
    usage_type:str
    quantity:int=Field(gt=0)
    idempotency_key:str=Field(min_length=1,max_length=200)
class GenerateIn(BaseModel):
    tenant_id:str
    prompt:str=Field(min_length=1,max_length=10000)
    input_tokens:int=Field(default=0,ge=0)
    cached_input_tokens:int=Field(default=0,ge=0)
    output_tokens:int=Field(default=0,ge=0)
    reasoning_tokens:int=Field(default=0,ge=0)
    idempotency_key:str=Field(min_length=1,max_length=200)
