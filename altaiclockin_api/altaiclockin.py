#!/usr/bin/env python3
"""
Altaiclockin Automation Script - API Version
=============================================

This version is used by the Docker API service.
It reads credentials from environment variables.

Usage:
    python3 altaiclockin.py checkin   # Clock in
    python3 altaiclockin.py checkout  # Clock out

Environment Variables (required):
    ALTAICLOCKIN_USERNAME - Your username
    ALTAICLOCKIN_PASSWORD - Your password
"""

import sys
import time
import random
import logging
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException, StaleElementReferenceException

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

def close_clause_modal(driver, _wait):
    """Close the clause/terms modal if it appears after login"""
    try:
        modal_bg = driver.find_element(By.ID, "cpContenidoCentral_mpClausula_backgroundElement")
        if modal_bg.is_displayed():
            logging.info("Clause modal detected, attempting to close it...")
            possible_buttons = [
                "cpContenidoCentral_btnAceptarClausula",
                "cpContenidoCentral_btnCerrarClausula",
                "cpContenidoCentral_btnOkClausula",
            ]
            for btn_id in possible_buttons:
                try:
                    btn = driver.find_element(By.ID, btn_id)
                    if btn.is_displayed():
                        logging.info(f"Clicking modal button: {btn_id}")
                        driver.execute_script("arguments[0].click();", btn)
                        human_sleep(2.0, 3.0)
                        return True
                except NoSuchElementException:
                    continue
            # Fallback: try to click modal OK via JavaScript
            try:
                modal = driver.find_element(By.ID, "cpContenidoCentral_mpClausula")
                ok_buttons = modal.find_elements(By.XPATH, ".//input[@type='submit' or @type='button'] | .//button | .//a[contains(@class,'btn')]")
                for btn in ok_buttons:
                    if btn.is_displayed():
                        logging.info("Clicking modal OK button via fallback search")
                        driver.execute_script("arguments[0].click();", btn)
                        human_sleep(2.0, 3.0)
                        return True
            except NoSuchElementException:
                pass
            logging.warning("Could not find modal close button")
    except NoSuchElementException:
        pass
    return False

def safe_click_element(driver, element, name="element"):
    """Click an element, handling intercepts by trying JS click as fallback"""
    try:
        element.click()
        logging.info(f"Clicked {name} (normal)")
    except ElementClickInterceptedException:
        logging.warning(f"Normal click intercepted on {name}, trying JavaScript click...")
        driver.execute_script("arguments[0].click();", element)
        logging.info(f"Clicked {name} (JavaScript)")

def find_and_click_action(driver, wait, action):
    """Find the action button (checkin/checkout) and click it, handling stale references"""
    button_id = "cpContenidoCentral_lnkbtnGeneralInicio" if action == "checkin" else "cpContenidoCentral_lnkbtnGeneralFin"
    logging.info(f"Looking for {action} button ({button_id})")
    
    for attempt in range(3):
        try:
            button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))
            human_sleep(0.5, 1.0)
            safe_click_element(driver, button, f"{action} button")
            human_sleep(2.0, 4.0)
            logging.info(f"Action '{action}' completed successfully!")
            return True
        except StaleElementReferenceException:
            logging.warning(f"Button became stale (attempt {attempt + 1}/3), retrying...")
            human_sleep(1.0, 2.0)
        except TimeoutException:
            logging.error(f"Timeout waiting for {action} button")
            raise
    
    raise Exception(f"Failed to click {action} button after 3 attempts")

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

    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        logging.info("Launching Firefox...")
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 15)

        logging.info(f"Navigating to {URL}")
        driver.get(URL)
        human_sleep(1.5, 3.0)

        logging.info("Trying to find login fields...")
        user_input = wait.until(EC.presence_of_element_located((By.ID, "txLoginUsuario")))
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

        human_sleep(3.0, 5.0)

        # Handle clause modal if present
        close_clause_modal(driver, wait)

        # Find and click the action button (with stale reference handling)
        find_and_click_action(driver, wait, action)

    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        if driver:
            try:
                driver.save_screenshot(f"error_screenshot_{int(time.time())}.png")
                logging.info("Screenshot saved for debugging")
            except Exception:
                pass
        raise  # Re-raise the exception so app.py can capture it
    finally:
        logging.info("Closing browser")
        if driver:
            driver.quit()
        logging.info("Script finished")

if __name__ == "__main__":
    main()
