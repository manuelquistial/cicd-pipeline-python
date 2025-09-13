"""
Flask web application for a secure calculator.

This module provides a web interface for performing basic arithmetic operations
(addition, subtraction, multiplication, division) with comprehensive security
features including CSRF protection, rate limiting, input validation, and
security headers.

Security Features:
    - CSRF protection using Flask-WTF
    - Rate limiting with Flask-Limiter
    - Input validation with WTForms
    - Security headers (X-Frame-Options, X-XSS-Protection, etc.)
    - Secure secret key management
    - Error handling without information disclosure

Environment Variables:
    SECRET_KEY: Flask secret key (required in production)
    FLASK_ENV: Environment mode (development/production)
    FLASK_DEBUG: Debug mode (true/false)
    CSRF_PROTECTION: Enable CSRF protection (true/false)
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import FloatField, SelectField, validators

from .calculadora import dividir, multiplicar, restar, sumar

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Security Configuration
SECRET_KEY_ENV_VAR = "SECRET_KEY"


def get_secret_key():
    """Get secret key from environment variable."""
    secret_key = os.getenv(SECRET_KEY_ENV_VAR)
    if not secret_key:
        raise ValueError(
            f"{SECRET_KEY_ENV_VAR} environment variable must be set. "
            "Generate one with: python -c 'import secrets; "
            + "print(secrets.token_hex(32))'"
        )
    return secret_key


app.config[SECRET_KEY_ENV_VAR] = get_secret_key()
app.config["WTF_CSRF_ENABLED"] = True
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # 1 hour

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"],
)


# Input validation form
class CalculatorForm(FlaskForm):
    """Form for calculator input validation.

    This form handles input validation for the calculator application,
    including number validation and operation selection.
    """

    num1 = FloatField(
        "Número 1",
        [
            validators.InputRequired(),
            validators.NumberRange(min=-1e10, max=1e10),
        ],
    )
    num2 = FloatField(
        "Número 2",
        [
            validators.InputRequired(),
            validators.NumberRange(min=-1e10, max=1e10),
        ],
    )
    operacion = SelectField(
        "Operación",
        choices=[
            ("sumar", "Sumar"),
            ("restar", "Restar"),
            ("multiplicar", "Multiplicar"),
            ("dividir", "Dividir"),
        ],
        validators=[validators.InputRequired()],
    )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for CI/CD."""
    return jsonify({"status": "healthy", "message": "Calculator app is running"})


def _validate_input_numbers(num1, num2):
    """Validate input numbers for security and format."""
    if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
        raise ValueError("Invalid number format")

    if abs(num1) > 1e10 or abs(num2) > 1e10:
        raise ValueError("Numbers too large")


def _perform_calculation(num1, num2, operacion):
    """Perform the requested calculation operation."""
    if operacion == "sumar":
        return sumar(num1, num2)
    if operacion == "restar":
        return restar(num1, num2)
    if operacion == "multiplicar":
        return multiplicar(num1, num2)
    if operacion == "dividir":
        return dividir(num1, num2)

    return "Operación no válida"


def _handle_calculation_error(exception):
    """Handle calculation errors and return appropriate error message."""
    if isinstance(exception, ValueError):
        return "Error: Introduce números válidos"
    if isinstance(exception, ZeroDivisionError):
        return "Error: No se puede dividir por cero"

    app.logger.error("Unexpected error in calculator: %s", exception)
    return "Error interno del servidor"


def _process_form_submission(form):
    """Process form submission and return result or error."""
    try:
        num1 = form.num1.data
        num2 = form.num2.data
        operacion = form.operacion.data

        _validate_input_numbers(num1, num2)
        resultado = _perform_calculation(num1, num2, operacion)
        return resultado, None

    except (ValueError, ZeroDivisionError) as e:
        error = _handle_calculation_error(e)
        return None, error
    except (TypeError, AttributeError, OverflowError) as e:
        # Handle specific calculation errors
        app.logger.error("Calculation error in form submission: %s", e)
        return None, "Error interno del servidor"
    except Exception as e:
        # Log truly unexpected errors but don't expose internal details
        app.logger.error("Unexpected error in form submission: %s", e)
        return None, "Error interno del servidor"


@app.route("/", methods=["GET"])
def index():
    """Display the calculator form page.

    Returns:
        str: Rendered HTML template with the calculator form
    """
    form = CalculatorForm()
    return render_template("index.html", form=form, resultado=None, error=None)


@app.route("/calculate", methods=["POST"])
def calculate():
    """Process calculator form submission.

    Returns:
        str: Rendered HTML template with the calculator form and result
    """
    form = CalculatorForm()
    resultado = None
    error = None

    if form.validate():
        resultado, error = _process_form_submission(form)
    else:
        # Form validation failed
        error = "Error: Datos de entrada inválidos"

    return render_template("index.html", form=form, resultado=resultado, error=error)


# Security configuration
@app.before_request
def restrict_http_methods():
    """Restrict HTTP methods to only allow safe methods"""
    allowed_methods = ["GET", "POST"]
    if request.method not in allowed_methods:
        return jsonify(error="Method not allowed"), 405
    return None


@app.after_request
def set_security_headers(response):
    """Add comprehensive security headers to all responses"""
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Force HTTPS in production
    if os.getenv("FLASK_ENV") == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        + "script-src 'self'; "
        + "style-src 'self' 'unsafe-inline'; "
        + "img-src 'self' data:; "
        + "font-src 'self'; "
        + "connect-src 'self'; "
        + "frame-ancestors 'none'; "
        + "base-uri 'self'; "
        + "form-action 'self'"
    )

    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Remove server information
    response.headers.pop("Server", None)

    return response


# Error handlers
@app.errorhandler(405)
def method_not_allowed_handler(_e):
    """Handle method not allowed errors"""
    return jsonify(error="Method not allowed"), 405


@app.errorhandler(429)
def ratelimit_handler(_e):
    """Handle rate limit exceeded"""
    return jsonify(error="Rate limit exceeded. Please try again later."), 429


@app.errorhandler(400)
def bad_request_handler(_e):
    """Handle bad requests"""
    return jsonify(error="Bad request"), 400


@app.errorhandler(500)
def internal_error_handler(e):
    """Handle internal server errors"""
    app.logger.error("Internal server error: %s", e)
    return jsonify(error="Internal server error"), 500


# Request size limit
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size

if __name__ == "__main__":  # pragma: no cover
    # Production settings
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, port=3000, host="0.0.0.0")
