from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
 
class UsuarioCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(..., min_length=2, max_length=60)   
    email: EmailStr                                       
 
class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str | None = Field(default=None, min_length=2, max_length=60)
    email: EmailStr | None = None
 
class UsuarioResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    fecha_registro: datetime