"""
Flask web application for a calculator.

This module provides a simple web interface for performing basic arithmetic
operations (addition, subtraction, multiplication, division) using a calculator
module.
"""

import os
from urllib.parse import urlparse

from flask import Flask, abort, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .calculadora import dividir, multiplicar, restar, sumar

app = Flask(__name__)

# Environment-based security configuration

ENVIRONMENT = os.getenv("FLASK_ENV", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=(
        ["200 per day", "50 per hour"]
        if IS_PRODUCTION
        else ["1000 per day", "200 per hour"]
    ),
)

# Disable rate limiting for testing
if os.getenv("TESTING") == "true":
    limiter.enabled = False


def validate_request_origin():
    """
    Validate that the request comes from the same origin.
    This provides basic protection against CSRF attacks.
    Only enabled in production environment.
    """
    if not IS_PRODUCTION:
        return  # Skip validation in development

    # Get the referer header
    referer = request.headers.get("Referer")
    if referer:
        # Extract the origin from referer
        referer_origin = urlparse(referer).netloc
        request_origin = request.headers.get("Host")

        # Allow requests from same origin
        if referer_origin != request_origin:
            abort(403, description="Invalid request origin")


@app.route("/", methods=["GET"])
@limiter.limit("10 per minute")  # Additional rate limiting for calculations
def index():
    """
    Handle the main calculator page.

    This function processes GET requests to display the calculator form
    and perform calculations via query parameters.

    Query Parameters:
        num1 (float): First number for calculation
        num2 (float): Second number for calculation
        operacion (str): Operation to perform (sumar, restar, multiplicar, dividir)

    Returns:
        str: Rendered HTML template with the calculator form and result.
    """
    # Validate request origin for CSRF protection
    validate_request_origin()

    resultado = None

    # Check if calculation parameters are provided
    if (
        request.args.get("num1")
        and request.args.get("num2")
        and request.args.get("operacion")
    ):
        try:
            num1 = float(request.args.get("num1"))
            num2 = float(request.args.get("num2"))
            operacion = request.args.get("operacion")

            if operacion == "sumar":
                resultado = sumar(num1, num2)
            elif operacion == "restar":
                resultado = restar(num1, num2)
            elif operacion == "multiplicar":
                resultado = multiplicar(num1, num2)
            elif operacion == "dividir":
                resultado = dividir(num1, num2)
            else:
                resultado = "Operación no válida"
        except ValueError:
            resultado = "Error: Introduce números válidos"
        except ZeroDivisionError:
            resultado = "Error: No se puede dividir por cero"

    return render_template("index.html", resultado=resultado)


if __name__ == "__main__":
    app.run(debug=False, port=3000, host="0.0.0.0")
