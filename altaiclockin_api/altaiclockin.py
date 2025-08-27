# Copy your functional altaiclockin.py script here
# You can overwrite this file with your updated version if you make improvements.

import sys
import time
import random
import logging
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

# --- CONFIGURATION ---
URL = "https://app.altaiclockin.com/"
USERNAME = os.getenv("ALTAICLOCKIN_USERNAME")
PASSWORD = os.getenv("ALTAICLOCKIN_PASSWORD")
# ----------------------

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

def human_sleep(a, b):
    delay = random.uniform(a, b)
    logging.debug(f"sleeping {delay:.2f}s")
    time.sleep(delay)

def main():
    # Validate that credentials are configured
    if not USERNAME or not PASSWORD:
        raise ValueError("ERROR: ALTAICLOCKIN_USERNAME and ALTAICLOCKIN_PASSWORD variables must be configured")
    
    if len(sys.argv) != 2:
        logging.error("Usage: python3 altaiclockin.py <checkin|checkout>")
        sys.exit(1)

    action = sys.argv[1].lower()
    if action not in ["checkin", "checkout"]:
        logging.error("Argument must be 'checkin' or 'checkout'")
        sys.exit(1)

    logging.info(f"Starting script with action: {action}")

    try:
        options = Options()
        options.add_argument("--headless")
        logging.info("Launching Firefox...")
        driver = webdriver.Firefox(options=options)

        logging.info(f"Navigating to {URL}")
        driver.get(URL)
        human_sleep(1.5, 3.0)

        logging.info("Trying to find login fields...")
        user_input = driver.find_element(By.ID, "txLoginUsuario")
        pass_input = driver.find_element(By.ID, "txLoginContrasena")

        logging.info("Entering username")
        for ch in USERNAME:
            user_input.send_keys(ch)
            time.sleep(random.uniform(0.05, 0.15))

        human_sleep(0.4, 1.0)

        logging.info("Entering password")
        for ch in PASSWORD:
            pass_input.send_keys(ch)
            time.sleep(random.uniform(0.05, 0.15))

        human_sleep(0.3, 0.8)

        logging.info("Clicking 'Login' button")
        driver.find_element(By.ID, "btnLogin").click()

        human_sleep(2.0, 4.0)

        logging.info("Looking for action button")
        if action == "checkin":
            button = driver.find_element(By.ID, "cpContenidoCentral_lnkbtnGeneralInicio")
        else:
            button = driver.find_element(By.ID, "cpContenidoCentral_lnkbtnGeneralFin")

        human_sleep(0.8, 2.0)
        logging.info("Clicking action button")
        button.click()
        human_sleep(2.0, 4.0)

    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        raise  # Re-raise the exception so app.py can capture it
    finally:
        logging.info("Closing browser")
        if 'driver' in locals():
            driver.quit()
        logging.info("Script finished")

if __name__ == "__main__":
    main()
