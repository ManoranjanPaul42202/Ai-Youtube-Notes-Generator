import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time


# ---------- FIXTURE TO START FLASK SERVER ----------
@pytest.fixture(scope="module")
def setup_server():
    # Start Flask app
    process = subprocess.Popen(["python", "app.py"])
    time.sleep(5)  # Wait for server to start
    yield
    process.terminate()


# ---------- FIXTURE TO CREATE DRIVER ----------
@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


# ---------- TEST: VALID LOGIN ----------
def test_valid_login(setup_server, driver):
    driver.get("http://localhost:5000/login")

    driver.find_element(By.NAME, "username").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


# ---------- TEST: INVALID LOGIN ----------
def test_invalid_login(driver):
    driver.get("http://localhost:5000/login")

    driver.find_element(By.NAME, "username").send_keys("wrong")
    driver.find_element(By.NAME, "password").send_keys("wrong123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    error_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    ).text

    assert "Invalid credentials" in error_message