# app/app.py
import os

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import FloatField, SelectField, validators

from .calculadora import dividir, multiplicar, restar, sumar

app = Flask(__name__)

# Security Configuration
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)
app.config["WTF_CSRF_ENABLED"] = True
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # 1 hour

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)


# Input validation form
class CalculatorForm(FlaskForm):
    num1 = FloatField(
        "Número 1",
        [validators.InputRequired(), validators.NumberRange(min=-1e10, max=1e10)],
    )
    num2 = FloatField(
        "Número 2",
        [validators.InputRequired(), validators.NumberRange(min=-1e10, max=1e10)],
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


@app.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Additional rate limiting for this endpoint
def index():
    form = CalculatorForm()
    resultado = None
    error = None

    if request.method == "POST" and form.validate():
        try:
            num1 = form.num1.data
            num2 = form.num2.data
            operacion = form.operacion.data

            # Additional security checks
            if not isinstance(num1, (int, float)) or not isinstance(num2, (int, float)):
                raise ValueError("Invalid number format")

            # Check for extremely large numbers that could cause issues
            if abs(num1) > 1e10 or abs(num2) > 1e10:
                raise ValueError("Numbers too large")

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
            error = "Error: Introduce números válidos"
        except ZeroDivisionError:
            error = "Error: No se puede dividir por cero"
        except Exception as e:
            error = "Error interno del servidor"
            app.logger.error(f"Unexpected error in calculator: {e}")
    elif request.method == "POST":
        # Form validation failed
        error = "Error: Datos de entrada inválidos"

    return render_template("index.html", form=form, resultado=resultado, error=error)


# Security headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"
    response.headers[
        "Content-Security-Policy"
    ] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify(error="Rate limit exceeded. Please try again later."), 429


@app.errorhandler(400)
def bad_request_handler(e):
    """Handle bad requests"""
    return jsonify(error="Bad request"), 400


@app.errorhandler(500)
def internal_error_handler(e):
    """Handle internal server errors"""
    app.logger.error(f"Internal server error: {e}")
    return jsonify(error="Internal server error"), 500


# Request size limit
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size

if __name__ == "__main__":  # pragma: no cover
    # Production settings
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, port=3000, host="0.0.0.0")
