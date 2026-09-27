"""
Centralized exception handlers, registered onto the FastAPI app.

Ensures every error response follows a consistent JSON shape:
{
    "success": false,
    "message": "<human readable message>",
    "details": <optional extra info>
}
"""

import logging

from fastapi import FastAPI,Request,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import DuplicateKeyError,PyMongoError

logger=logging.getLogger("worksphere.errors")

def register_exceptional_handlers(app:FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request:Request,exc:StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success":False,"messege":exc.detail,"details":None},
            headers=getattr(exc,"headers",None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request:Request,exc:RequestValidationError):
        errors=[
            {"field":".".join(str(loc) for loc in err["loc"] if loc!="body"),"messege":err["msg"] } for err in exc.errors()
        ]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success":False,
                "messege":"Validation failed for one or more fields",
                "details":errors,
            },
        )

    @app.exception_handler(DuplicateKeyError)

    def duplicate_key_handler(request:Request,exc:DuplicateKeyError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                'sucess':False,
                "messege":"A record with this unique field already exists",
                "details":None,
            },
        )
    
    @app.exception_handler(PyMongoError)
    async def pymongo_error_handler(request:Request,exc:PyMongoError):
        logger.error("Database error: %s",exc)

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                'success':False,
                "messege":"A database error occured,please try again later",
                "details":None,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request:Request,exc:Exception):
      logger.exception("Unhandled exception: %s", exc)
      return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An unexpected error occurred",
                "details": None,
            },
        )

