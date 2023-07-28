import random
import string

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


def random_str():
    N = random.randint(10, 50)
    return ''.join(random.choices(list(string.ascii_uppercase + string.digits) + ['Sale', 'SALE', 'sale', 'sAlE'], k=N))


def generate_big_file():
    with open('Big.csv', 'wb') as f:
        for line in range(10 ** 7):
            f.write(f'{line}, {random_str() + random.choices(("sale", ""))[0]}, ' \
                    f'{random_str() + random.choices(("sale", ""))[0]}, ' \
                    f'{random.randint(100, 10000)}\n'.encode())


@app.get("/get_csv/")
def root():
    return FileResponse('Big.csv')
