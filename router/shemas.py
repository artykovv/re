from pydantic import BaseModel

class CreateTable(BaseModel):
    uuid: str
    name: str
    description: str
    price: str
    link: str
    quantity: str

