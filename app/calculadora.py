"""
Calculator module for basic arithmetic operations.

This module provides functions for performing basic arithmetic operations
including addition, subtraction, multiplication, and division with
appropriate error handling for division by zero.
"""


def sumar(a, b):
    """
    Add two numbers.

    Args:
        a (float): First number to add.
        b (float): Second number to add.

    Returns:
        float: The sum of a and b.
    """
    return a + b


def restar(a, b):
    """
    Subtract two numbers.

    Args:
        a (float): Number to subtract from.
        b (float): Number to subtract.

    Returns:
        float: The difference of a and b.
    """
    return a - b


def multiplicar(a, b):
    """
    Multiply two numbers.

    Args:
        a (float): First number to multiply.
        b (float): Second number to multiply.

    Returns:
        float: The product of a and b.
    """
    return a * b


def dividir(a, b):
    """
    Divide two numbers.

    Args:
        a (float): Dividend (number to be divided).
        b (float): Divisor (number to divide by).

    Returns:
        float: The quotient of a and b.

    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a / b
