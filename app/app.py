"""
Flask web application for a calculator.

This module provides a simple web interface for performing basic arithmetic
operations (addition, subtraction, multiplication, division) using a calculator
module.
"""

from flask import Flask, render_template, request
from .calculadora import sumar, restar, multiplicar, dividir

app = Flask(__name__)


@app.route("/", methods=["GET"])
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
    resultado = None
    
    # Check if calculation parameters are provided
    if request.args.get("num1") and request.args.get("num2") and request.args.get("operacion"):
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
