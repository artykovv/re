from fastapi import FastAPI
from router.router import router as router_product

app  = FastAPI()

app.include_router(router_product)