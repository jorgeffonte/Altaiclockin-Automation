#!/usr/bin/env python3
"""
Altaiclockin Automation Script - Standalone Version
==================================================

This is a standalone version that can be run manually without Docker or API.
It uses environment variables for credentials or falls back to hardcoded values.

Usage:
    python3 altaiclockin.py checkin   # Clock in
    python3 altaiclockin.py checkout  # Clock out

Environment Variables (optional):
    ALTAICLOCKIN_USERNAME - Your username
    ALTAICLOCKIN_PASSWORD - Your password

Requirements:
    pip install selenium webdriver-manager
"""

import sys
import time
import random
import logging
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
URL = "https://app.altaiclockin.com/"

# Try to get credentials from environment variables, fallback to hardcoded values
USERNAME = os.getenv("ALTAICLOCKIN_USERNAME")
PASSWORD = os.getenv("ALTAICLOCKIN_PASSWORD")
# ---------------------

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

def human_sleep(min_seconds, max_seconds):
    """Sleep for a random amount of time to simulate human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    logging.debug(f"Sleeping {delay:.2f}s")
    time.sleep(delay)

def type_text_humanly(element, text):
    """Type text character by character with random delays"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def main():
    if len(sys.argv) != 2:
        logging.error("Usage: python3 altaiclockin.py <checkin|checkout>")
        logging.error("  checkin  - Clock in")
        logging.error("  checkout - Clock out")
        sys.exit(1)

    action = sys.argv[1].lower()
    if action not in ["checkin", "checkout"]:
        logging.error("Argument must be 'checkin' (clock in) or 'checkout' (clock out)")
        sys.exit(1)

    # Validate that credentials are configured
    if not USERNAME or not PASSWORD:
        logging.error("Credentials not configured. Set ALTAICLOCKIN_USERNAME and ALTAICLOCKIN_PASSWORD environment variables")
        sys.exit(1)

    logging.info(f"Starting script with action: {action}")
    logging.info(f"Using username: {USERNAME}")

    driver = None
    try:
        options = Options()
        options.add_argument("--headless")  # Run in headless mode for automation
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        logging.info("Launching Firefox...")
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1920, 1080)
        
        wait = WebDriverWait(driver, 10)

        logging.info(f"Navigating to {URL}")
        driver.get(URL)
        human_sleep(1.5, 3.0)

        logging.info("Looking for login fields...")
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txLoginUsuario")))
        pass_input = driver.find_element(By.ID, "txLoginContrasena")

        logging.info("Typing username")
        type_text_humanly(user_input, USERNAME)
        human_sleep(0.4, 1.0)

        logging.info("Typing password")
        type_text_humanly(pass_input, PASSWORD)
        human_sleep(0.3, 0.8)

        logging.info("Clicking 'Sign in' button")
        login_button = driver.find_element(By.ID, "btnLogin")
        login_button.click()
        human_sleep(2.0, 4.0)

        logging.info("Looking for action button")
        if action == "checkin":
            logging.info("Looking for clock-in button")
            button = wait.until(EC.element_to_be_clickable((By.ID, "cpContenidoCentral_lnkbtnGeneralInicio")))
        else:
            logging.info("Looking for clock-out button")
            button = wait.until(EC.element_to_be_clickable((By.ID, "cpContenidoCentral_lnkbtnGeneralFin")))

        logging.info("Clicking action button")
        button.click()
        human_sleep(2.0, 4.0)

        logging.info(f"Action '{action}' completed successfully!")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if driver:
            try:
                # Take a screenshot for debugging
                driver.save_screenshot(f"error_screenshot_{int(time.time())}.png")
                logging.info("Screenshot saved for debugging")
            except:
                pass
        raise  # Re-raise the exception for proper error handling

    finally:
        if driver:
            logging.info("Closing browser")
            driver.quit()
        logging.info("Script finished")

if __name__ == "__main__":
    main()
