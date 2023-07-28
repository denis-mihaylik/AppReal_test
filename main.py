import os
from collections import namedtuple
from dataclasses import dataclass
from io import BytesIO
from multiprocessing.pool import Pool

import aiohttp
import fastapi
from fastapi import FastAPI
from pydantic import BaseModel


class CatalogueForm(BaseModel):
    catalogue_url: str


RECORD_END = '\n'
CHUNK_SIZE = 1024*64

app = FastAPI()

struct = namedtuple("Headers", "id, title, description, price")

@dataclass
class Product:
    id: int
    sold: bool = False


class MockDB:
    def get(self, id):
        return Product(id)

    def commit(self):
        pass

    def delete(self):
        pass


def retrieve_product(id):
    product = MockDB().get(id)
    return product


def mark_as_sold(product: Product):
    product.sold = True
    MockDB().commit()


async def get_chunk_data(content: aiohttp.StreamReader):
    """Ensure consistency data"""
    pre_data = await content.read(CHUNK_SIZE)
    if pre_data:
        pre_data += await content.readuntil(RECORD_END.encode())  # read until new line
        return pre_data


def process(chunked_data: bytes):
    """Would be nice to check for input chunk of data"""
    db_connection = MockDB()
    for filtered_record in filter_records(chunked_data):
        # mocked process for DB
        retrieved_product = retrieve_product(filtered_record.id)
        retrieved_product.sold = True
        db_connection.delete()
        db_connection.commit()


def filter_records(chunk_data: bytes) -> struct:
    """Generator that filters records"""
    buf = BytesIO(chunk_data)
    for raw_record in buf.readlines():
        try:
            record = struct(*map(bytes.strip, raw_record.split(b',')))
        except Exception:
            print('Bad row. Inconsistency with expected schema')
            continue
        if b"sale" in record.title.lower() or b"sale" in record.description.lower():
            yield record


@app.post("/read_catalogue_from_url/")
async def root(cat_form: CatalogueForm):
    url = cat_form.catalogue_url

    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        with Pool(os.cpu_count() - 1) as pool:
            chunked_data = response.status == 200
            while chunked_data:
                chunk_data  = await get_chunk_data(response.content)
                if not chunk_data:
                    return fastapi.Response()
                # process(chunk_data)
                pool.apply_async(process, (chunk_data,))
