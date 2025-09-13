"""
Flask web application for a calculator.

This module provides a simple web interface for performing basic arithmetic
operations (addition, subtraction, multiplication, division) using a calculator
module.
"""

from flask import Flask, render_template, request
from .calculadora import sumar, restar, multiplicar, dividir

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Handle the main calculator page.

    This function processes both GET and POST requests to the root route.
    For GET requests, it displays the calculator form.
    For POST requests, it processes the form data, performs the requested
    arithmetic operation, and returns the result.

    Returns:
        str: Rendered HTML template with the calculator form and result.
    """
    resultado = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operacion = request.form["operacion"]

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
    app.run(debug=True, port=3000, host="0.0.0.0")
