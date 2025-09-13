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
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--window-size=1920,1080")
    # Additional options for CI environment
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    
    driver = webdriver.Chrome(options=options)
    # Set longer timeouts for CI environment
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)

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
    
    # Try multiple times with increasing delays for CI environment
    for attempt in range(3):
        print(f"DEBUG: Attempt {attempt + 1}/3 to get result")
        
        # Wait with increasing delay
        wait_time = 2 + (attempt * 2)  # 2s, 4s, 6s
        print(f"DEBUG: Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        
        # Debug: Print current state
        print(f"DEBUG: Current URL: {browser.current_url}")
        print(f"DEBUG: Page title: {browser.title}")
        print(f"DEBUG: Looking for elements...")
        
        # Try to find elements immediately first
        result_elements = browser.find_elements(By.CLASS_NAME, "result")
        print(f"DEBUG: Found {len(result_elements)} result elements")
        if result_elements:
            print(f"DEBUG: Result text: '{result_elements[0].text}'")
            return result_elements[0].text

        # Check for general error first (higher priority)
        error_elements = browser.find_elements(By.CLASS_NAME, "error")
        print(f"DEBUG: Found {len(error_elements)} error elements")
        if error_elements:
            print(f"DEBUG: Error text: '{error_elements[0].text}'")
            return error_elements[0].text

        # Check for field validation errors
        field_errors = browser.find_elements(By.CLASS_NAME, "field-error")
        print(f"DEBUG: Found {len(field_errors)} field error elements")
        if field_errors:
            print(f"DEBUG: Field error text: '{field_errors[0].text}'")
            return field_errors[0].text
        
        print(f"DEBUG: No elements found in attempt {attempt + 1}")
        if attempt < 2:  # Not the last attempt
            print("DEBUG: Retrying...")
            continue
    
    # If no elements found immediately, wait for them
    print("DEBUG: Waiting for elements with WebDriverWait...")
    try:
        WebDriverWait(browser, 20).until(  # Increased timeout for CI
            lambda driver: driver.find_elements(By.CLASS_NAME, "result")
            or driver.find_elements(By.CLASS_NAME, "error")
            or driver.find_elements(By.CLASS_NAME, "field-error")
        )
        print("DEBUG: WebDriverWait completed successfully")

        # Check for result first
        result_elements = browser.find_elements(By.CLASS_NAME, "result")
        print(f"DEBUG: After wait - Found {len(result_elements)} result elements")
        if result_elements:
            print(f"DEBUG: After wait - Result text: '{result_elements[0].text}'")
            return result_elements[0].text

        # Check for error messages
        error_elements = browser.find_elements(By.CLASS_NAME, "error")
        print(f"DEBUG: After wait - Found {len(error_elements)} error elements")
        if error_elements:
            print(f"DEBUG: After wait - Error text: '{error_elements[0].text}'")
            return error_elements[0].text

        # Check for field validation errors
        field_errors = browser.find_elements(By.CLASS_NAME, "field-error")
        print(f"DEBUG: After wait - Found {len(field_errors)} field error elements")
        if field_errors:
            print(f"DEBUG: After wait - Field error text: '{field_errors[0].text}'")
            return field_errors[0].text

        print("DEBUG: No elements found after WebDriverWait")
        return "No se encontró resultado ni error"
    except TimeoutException:
        # Debug information for CI
        print(f"Timeout waiting for elements. Current URL: {browser.current_url}")
        print(f"Page title: {browser.title}")
        print(f"Page source preview: {browser.page_source[:500]}...")
        
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

    # Add longer delay between tests to avoid rate limiting (increased for CI)
    time.sleep(8)

    browser.get(BASE_URL)

    # Wait for page to load with longer timeout (increased for CI)
    try:
        WebDriverWait(browser, 45).until(  # Increased timeout for CI
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
    except TimeoutException:
        # Debug information for CI
        print(f"Form loading timeout. Current URL: {browser.current_url}")
        print(f"Page title: {browser.title}")
        print(f"Page source preview: {browser.page_source[:500]}...")
        
        # If form not found, check if page loaded at all
        if "Calculadora Segura" not in browser.page_source:
            raise Exception("Page did not load properly")
        # Try to find form again
        form_elements = browser.find_elements(By.TAG_NAME, "form")
        if not form_elements:
            raise Exception("Form not found on page")

    # Additional delay to ensure page is fully loaded (increased for CI)
    time.sleep(5)

    # Encuentra los elementos de la página.  Esta vez con la funcion auxiliar.
    num1_input, num2_input, operacion_select, calcular_button = find_elements(browser)

    # Realiza la operacion:
    print(f"DEBUG: Filling form with num1='{num1}', num2='{num2}', operacion='{operacion}'")
    num1_input.clear()
    num1_input.send_keys(num1)
    num2_input.clear()
    num2_input.send_keys(num2)
    operacion_select.select_by_value(operacion)
    
    print("DEBUG: Clicking calculate button...")
    calcular_button.click()

    # Wait for page to reload after form submission (increased for CI)
    print("DEBUG: Waiting for page to reload...")
    time.sleep(3)

    # Verifica con la funcion auxiliar:
    print(f"DEBUG: Expected result: '{resultado_esperado}'")
    actual_result = get_resultado(browser)
    print(f"DEBUG: Actual result: '{actual_result}'")
    assert resultado_esperado in actual_result
