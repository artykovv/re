from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from sqlalchemy import select, insert, update
from router.models import Table
from router.shemas import CreateTable
from typing import List
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
import io
from fastapi.responses import FileResponse



router = APIRouter(prefix="/api/v1/products",)

@router.get("/get/product")
async def get_product(
    uuid: str,
    session: AsyncSession = Depends(get_async_session)
    ):
    query = select(Table).where(Table.uuid == uuid)
    result = await session.execute(query)
    data = result.scalar()
    return data

@router.get("/get/all")
async def get_all_products(session: AsyncSession = Depends(get_async_session)):
    query = select(Table)
    result = await session.execute(query)
    data = result.scalars().all()

    # Создаем новый Workbook для Excel
    wb = Workbook()
    ws = wb.active

    # Добавляем заголовки
    ws.append(["uuid", "name", "description", "price","link", "quantity"])

    # Добавляем данные
    for product in data:
        ws.append([product.uuid, product.name, product.description, product.price, product.link, product.quantity])

    # Сохраняем Workbook во временный файл
    temp_file = "/tmp/products.xlsx"  # Можно использовать временное имя файла
    wb.save(temp_file)

    # Отправляем файл как HTTP-ответ
    return FileResponse(temp_file, filename="products.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



@router.get("/get/product/quantity")
async def get_product_quantity(
    uuid: str,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Table).where(Table.uuid == uuid)
    result = await session.execute(query)
    data = result.scalar()
    quantity_value = data.quantity
    return quantity_value


@router.post("/upload")
async def upload_file_and_update_db(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session)
):
    if not file.filename.endswith(".xlsx"):
        return {"detail": "Неверный формат файла. Разрешены только файлы .xlsx."}

    try:
        data = await file.read()
        df = pd.read_excel(BytesIO(data))

        # Убедимся, что столбец 'uuid' имеет строковый тип данных
        df['uuid'] = df['uuid'].astype(str)

        async with session.begin():
            for _, row in df.iterrows():
                # Преобразуем значение 'price' в строку
                row['price'] = str(row['price'])

                # Проверяем, существует ли запись по 'uuid'
                existing_record = await session.execute(
                    select(Table).where(Table.uuid == row['uuid'])
                )
                existing_record = existing_record.scalar()

                if existing_record:
                    # Обновляем существующую запись
                    existing_record.name = row['name']
                    existing_record.description = row['description']
                    existing_record.price = row['price']
                    existing_record.link = row['link']
                    existing_record.quantity = row['quantity']
                else:
                    # Создаем новую запись
                    new_record = Table(**row)
                    session.add(new_record)
        
        return {"detail": "Файл успешно загружен, база данных обновлена."}

    except Exception as e:
        return {"detail": f"Ошибка при обработке файла: {str(e)}"}