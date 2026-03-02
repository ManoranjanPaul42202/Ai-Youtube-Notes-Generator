import pytest
import sys
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="module")
def setup_server():
    process = subprocess.Popen([sys.executable, "run.py"])
    time.sleep(5)
    yield
    process.terminate()


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def test_valid_login(setup_server, driver):
    driver.get("http://localhost:5000/login")

    driver.find_element(By.NAME, "username").send_keys("admin@gmail.com")
    driver.find_element(By.NAME, "password").send_keys("admin123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


def test_invalid_login(setup_server, driver):
    driver.get("http://localhost:5000/login")

    driver.find_element(By.NAME, "username").send_keys("wrong")
    driver.find_element(By.NAME, "password").send_keys("wrong123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    error_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    ).text

    assert "Invalid credentials" in error_message