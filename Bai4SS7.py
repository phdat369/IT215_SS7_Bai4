from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

app = FastAPI()

orders = {
    1: {
        "id": 1,
        "code": "SP001",
        "payment_status": "PAID",
        "method": "BANK_TRANSFER"
    },
    2: {
        "id": 2,
        "code": "SP002",
        "payment_status": "UNPAID",
        "method": "NONE"
    }
}


class BaseResponse(BaseModel):
    status_code: int
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    time_stamp: str
    path: str


def create_response(
    request: Request,
    status_code: int,
    message: str,
    data=None,
    error=None
):
    return BaseResponse(
        status_code=status_code,
        message=message,
        data=data,
        error=error,
        time_stamp=datetime.now().isoformat(),
        path=request.url.path
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response = create_response(
        request=request,
        status_code=exc.status_code,
        message="Failed",
        error=exc.detail
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    response = create_response(
        request=request,
        status_code=500,
        message="Failed",
        error="Internal Server Error"
    )

    return JSONResponse(
        status_code=500,
        content=response.model_dump()
    )


@app.get("/orders/{order_id}/payment")
def get_payment(order_id: int, request: Request):

    if order_id not in orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return create_response(
        request=request,
        status_code=status.HTTP_200_OK,
        message="Success",
        data={
            "payment_status": orders[order_id]["payment_status"],
            "method": orders[order_id]["method"]
        }
    )

@app.get("/crash")
def crash():
    x = 10 / 0
    return x