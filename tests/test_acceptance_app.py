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
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


# Función de ayuda para esperar y obtener el resultado
def get_resultado(browser):
    import time
    
    # Simple wait for page to process
    time.sleep(1)
    
    # Try to find elements
    result_elements = browser.find_elements(By.CLASS_NAME, "result")
    if result_elements:
        return result_elements[0].text

    error_elements = browser.find_elements(By.CLASS_NAME, "error")
    if error_elements:
        return error_elements[0].text

    field_errors = browser.find_elements(By.CLASS_NAME, "field-error")
    if field_errors:
        return field_errors[0].text
    
    # Simple wait for elements
    try:
        WebDriverWait(browser, 10).until(
            lambda driver: driver.find_elements(By.CLASS_NAME, "result")
            or driver.find_elements(By.CLASS_NAME, "error")
            or driver.find_elements(By.CLASS_NAME, "field-error")
        )
        
        result_elements = browser.find_elements(By.CLASS_NAME, "result")
        if result_elements:
            return result_elements[0].text

        error_elements = browser.find_elements(By.CLASS_NAME, "error")
        if error_elements:
            return error_elements[0].text

        field_errors = browser.find_elements(By.CLASS_NAME, "field-error")
        if field_errors:
            return field_errors[0].text

        return "No se encontró resultado ni error"
    except TimeoutException:
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
def test_calculadora(browser, num1, num2, operacion, resultado_esperado):
    import time
    
    browser.get(BASE_URL)

    # Wait for page to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "form"))
    )

    # Find form elements
    num1_input, num2_input, operacion_select, calcular_button = find_elements(browser)

    # Fill and submit form
    num1_input.clear()
    num1_input.send_keys(num1)
    num2_input.clear()
    num2_input.send_keys(num2)
    operacion_select.select_by_value(operacion)
    calcular_button.click()

    # Wait for result
    time.sleep(1)

    # Check result
    actual_result = get_resultado(browser)
    assert resultado_esperado in actual_result
