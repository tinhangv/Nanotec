"""Module defining custom exceptions and helper methods to manage the server's
errors.

This made this package dependent on Flask as a web server but it ease the
creation of server for new projects.
"""
import json

from connexion.exceptions import ProblemException
from flask import Flask, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from alibrary.logger import logger


class CustomHttpError(RuntimeError):
    """Custom HTTP error raised by the server.

    This class will be specified to cover typical HTTP error code.
    """

    def __init__(self, message: str, code: int) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class BadRequestError(CustomHttpError):
    """Error raised in case of Bad Request, when the provided arguments are not
    valid
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"[BAD REQUEST] {message}", 400)


class NotFoundError(CustomHttpError):
    """Error raised in case of Not Found, when the requested resource does not
    exist
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"[NOT FOUND] {message}", 404)


class ConflictError(CustomHttpError):
    """Error raised in case of Conflict, when the request conflicts with the
    current server state
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"[CONFLICT] {message}", 409)


class InternalServerError(CustomHttpError):
    """Error raised in case of Internal Server Error, when the server
    encounters a runtime error
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"[INTERNAL SERVER ERROR] {message}", 500)


def custom_error_handler(error) -> Response:
    """Handles an error and returns the appropriate Flask Response.

    Args:
        error: An exception thrown by the server

    Returns:
        A Response object with the error message
    """
    if isinstance(error, CustomHttpError):
        return Response(
            response=json.dumps({
                "status_code": error.code,
                "message": error.message
            }),
            status=error.code,
            mimetype="application/json",
        )
    if isinstance(error, HTTPException):
        return Response(
            response=json.dumps({
                "status_code": error.code,
                "message": error.description
            }),
            status=error.code,
            mimetype="application/json",
        )
    if isinstance(error, ProblemException):
        return Response(
            response=json.dumps({
                "status_code":
                error.status,
                "message":
                f"[{error.title.upper()}] {error.detail}"
            }),
            status=error.status,
            mimetype="application/json",
        )

    return Response(
        response=json.dumps({
            "status_code": 500,
            "message": "UNKNOWN ERROR"
        }),
        status=500,
        mimetype="application/json",
    )

def enable_cors(app: Flask):
    CORS(app)
    logger.debug("CORS enabled")
