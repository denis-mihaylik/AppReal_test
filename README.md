# AppReal_test
1. In production I would make a separate service that will download files and process them. Or use rabbitMQ + Celery. (I'd prefer the first option)
2. There is one more file test_serv.py that contains a helping test functions.
generate_big_file() creates a CSV file with random string that may or may not contain sale word
Also there is simplest server that returns file generated by previous function
3. fastAPI. I chose it just to show a combination of async + multiprocessing. The same thing can be done by flask/Django/aiohttp etc.
example:
install fastapi: pip install fastapi uvicorn
generate helping file:
```
from test_serv import generate_big_file
generate_big_file()
```
the size can be changed inside the file. line 17
run it: > uvicorn test_serv:app --port 8001
4. Build docker container with exposed port 8000
or
5. run by: > uvicorn main:app --port 8000
open url: http://localhost:8000/docs
The Swagger will help
