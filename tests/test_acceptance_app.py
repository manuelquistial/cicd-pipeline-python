import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:3000")


# Configuración del driver (elige uno: Chrome o Firefox)
@pytest.fixture
def browser():
    # Opción 1: Chrome (headless - sin interfaz gráfica)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecuta sin interfaz gráfica
    options.add_argument("--no-sandbox")  # Necesario para algunos entornos
    options.add_argument("--disable-dev-shm-usage")  # Necesario para algunos entornos
    driver = webdriver.Chrome(options=options)

    # Opción 2: Firefox (headless)
    # options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    # driver = webdriver.Firefox(options=options)

    # Opción 3: Chrome (con interfaz gráfica - para depuración local)
    # driver = webdriver.Chrome()

    # Opción 4: Firefox (con interfaz gráfica)
    # driver = webdriver.Firefox()
    yield driver
    driver.quit()


# Función de ayuda para esperar y obtener el resultado
def get_resultado(browser):
    import time
    
    # First, wait a bit for the page to process
    time.sleep(1)
    
    # Try to find elements immediately first
    result_elements = browser.find_elements(By.CLASS_NAME, "result")
    if result_elements:
        return result_elements[0].text

    error_elements = browser.find_elements(By.CLASS_NAME, "error")
    if error_elements:
        return error_elements[0].text

    field_errors = browser.find_elements(By.CLASS_NAME, "field-error")
    if field_errors:
        return field_errors[0].text
    
    # If no elements found immediately, wait for them
    try:
        WebDriverWait(browser, 10).until(
            lambda driver: driver.find_elements(By.CLASS_NAME, "result")
            or driver.find_elements(By.CLASS_NAME, "error")
            or driver.find_elements(By.CLASS_NAME, "field-error")
        )

        # Check for result first
        result_elements = browser.find_elements(By.CLASS_NAME, "result")
        if result_elements:
            return result_elements[0].text

        # Check for error messages
        error_elements = browser.find_elements(By.CLASS_NAME, "error")
        if error_elements:
            return error_elements[0].text

        # Check for field validation errors
        field_errors = browser.find_elements(By.CLASS_NAME, "field-error")
        if field_errors:
            return field_errors[0].text

        return "No se encontró resultado ni error"
    except TimeoutException:
        # Final check if elements are present
        result_elements = browser.find_elements(By.CLASS_NAME, "result")
        if result_elements:
            return result_elements[0].text

        error_elements = browser.find_elements(By.CLASS_NAME, "error")
        if error_elements:
            return error_elements[0].text

        field_errors = browser.find_elements(By.CLASS_NAME, "field-error")
        if field_errors:
            return field_errors[0].text

        return "Error: Tiempo de espera agotado esperando el resultado."


# Funcion auxiliar para encontrar elementos:
def find_elements(browser):
    # The new form uses WTForms which generates different IDs
    num1_input = browser.find_element(By.ID, "num1")
    num2_input = browser.find_element(By.ID, "num2")
    operacion_select = Select(browser.find_element(By.ID, "operacion"))
    calcular_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    return num1_input, num2_input, operacion_select, calcular_button


@pytest.mark.parametrize(
    "num1, num2, operacion, resultado_esperado",
    [
        ("2", "3", "sumar", "Resultado: 5.0"),
        ("5", "2", "restar", "Resultado: 3.0"),
        ("4", "6", "multiplicar", "Resultado: 24.0"),
        ("10", "2", "dividir", "Resultado: 5.0"),
        ("5.0", "0.0", "dividir", "Error: No se puede dividir por cero"),
        ("abc", "def", "sumar", "Error: Datos de entrada inválidos"),
    ],
)
@pytest.mark.slow
def test_calculadora(browser, num1, num2, operacion, resultado_esperado):
    import time

    # Add delay between tests to avoid rate limiting
    time.sleep(3)

    browser.get(BASE_URL)

    # Wait for page to load with longer timeout
    WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "form"))
    )

    # Additional delay to ensure page is fully loaded
    time.sleep(3)

    # Encuentra los elementos de la página.  Esta vez con la funcion auxiliar.
    num1_input, num2_input, operacion_select, calcular_button = find_elements(browser)

    # Realiza la operacion:
    num1_input.clear()
    num1_input.send_keys(num1)
    num2_input.clear()
    num2_input.send_keys(num2)
    operacion_select.select_by_value(operacion)
    calcular_button.click()

    # Wait for page to reload after form submission
    time.sleep(2)

    # Verifica con la funcion auxiliar:
    assert resultado_esperado in get_resultado(browser)
