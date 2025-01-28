import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import uvicorn

from app.api import router
from app.exception import CustomException
from app.session import init_db, init_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await init_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logging.info(str(exc))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.message),
        },
    )


app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
