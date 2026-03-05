from pydantic import BaseModel


class ServiceInfoSchema(BaseModel):
    version: str
    project_name: str


class HealthSchema(BaseModel):
    db: bool


class OKSchema(BaseModel):
    OK: bool = True
