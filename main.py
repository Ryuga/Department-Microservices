
import asyncio
from uvicorn.main import run
from tortoise.contrib.starlette import register_tortoise

from fastapi.applications import FastAPI
from starlette.config import Config
from backend.services.background_service import post_transaction_microservice

config = Config('.env')
DEBUG = config('DEBUG', cast=bool, default=False)
host = "0.0.0.0"
port = 8000
redis_conn = None
if DEBUG:
    host = "127.0.0.1"
    port = 7000

app = FastAPI(debug=DEBUG)
register_tortoise(
    app,
    db_url=config("DB_URI"),
    modules={"models": ["backend.models"]},
    generate_schemas=False
)


@app.on_event("startup")
async def run_tasks():
    loop = asyncio.get_event_loop()
    loop.create_task(post_transaction_microservice())


if __name__ == "__main__":
    run("main:app", reload=True, host=host, port=port, forwarded_allow_ips='*', proxy_headers=True)
