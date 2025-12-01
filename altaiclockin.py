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
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException, TimeoutException

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

def safe_selenium_operation(operation, operation_name, max_retries=3):
    """
    Safely execute any Selenium operation with retry logic for marionette errors.
    
    This function handles the 'Failed to decode response from marionette' error
    that can occur during any WebDriver operation (find_element, click, etc.)
    
    Args:
        operation: A callable that performs the Selenium operation
        operation_name: Human-readable name for logging
        max_retries: Maximum number of retry attempts
        
    Returns:
        The result of the operation if successful
        
    Raises:
        Exception: If all retry attempts fail
    """
    last_exception = None
    for attempt in range(max_retries):
        try:
            return operation()
        except (WebDriverException, TimeoutException) as e:
            error_msg = str(e)
            last_exception = e
            
            # Check if it's the marionette decode error
            if "Failed to decode response from marionette" in error_msg:
                logging.warning(f"Attempt {attempt + 1}/{max_retries} failed for {operation_name}: {error_msg[:100]}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 1.0 * (2 ** attempt)
                    logging.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"All {max_retries} attempts failed for {operation_name}")
                    raise Exception(f"Failed {operation_name} after {max_retries} attempts due to marionette error") from e
            else:
                # Different error, re-raise immediately
                raise
    
    # Should not reach here, but just in case
    if last_exception:
        raise last_exception

def safe_click_element(driver, element, element_name, max_retries=3):
    """
    Safely click an element with retry logic and fallback to JavaScript click.
    
    This function handles the 'Failed to decode response from marionette' error
    by implementing:
    1. Retry logic with exponential backoff
    2. JavaScript click as fallback
    3. Better error handling
    
    Args:
        driver: Selenium WebDriver instance
        element: WebElement to click
        element_name: Human-readable name for logging
        max_retries: Maximum number of retry attempts
        
    Raises:
        Exception: If all retry attempts fail
    """
    for attempt in range(max_retries):
        try:
            # Ensure element is in view and ready
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.3)  # Brief pause after scroll
            
            # Try standard click
            element.click()
            logging.info(f"Successfully clicked {element_name}")
            return
            
        except (WebDriverException, ElementClickInterceptedException) as e:
            error_msg = str(e)
            
            # Check if it's the marionette decode error or click intercepted
            if "Failed to decode response from marionette" in error_msg or "ElementClickInterceptedException" in error_msg:
                logging.warning(f"Attempt {attempt + 1}/{max_retries} failed for {element_name}: {error_msg[:100]}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 0.5s, 1s, 2s
                    wait_time = 0.5 * (2 ** attempt)
                    logging.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Last attempt: try JavaScript click
                    logging.warning(f"Standard click failed after {max_retries} attempts, trying JavaScript click...")
                    try:
                        driver.execute_script("arguments[0].click();", element)
                        logging.info(f"Successfully clicked {element_name} using JavaScript")
                        return
                    except Exception as js_error:
                        logging.error(f"JavaScript click also failed: {js_error}")
                        raise Exception(f"Failed to click {element_name} after all retry attempts") from e
            else:
                # Different error, re-raise immediately
                raise

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
        human_sleep(2.0, 4.0)  # Increased wait for page load

        logging.info("Looking for login fields...")
        user_input = safe_selenium_operation(
            lambda: wait.until(EC.presence_of_element_located((By.ID, "txLoginUsuario"))),
            "find login username field"
        )
        pass_input = safe_selenium_operation(
            lambda: driver.find_element(By.ID, "txLoginContrasena"),
            "find login password field"
        )

        logging.info("Typing username")
        type_text_humanly(user_input, USERNAME)
        human_sleep(0.4, 1.0)

        logging.info("Typing password")
        type_text_humanly(pass_input, PASSWORD)
        human_sleep(0.3, 0.8)

        logging.info("Clicking 'Sign in' button")
        login_button = safe_selenium_operation(
            lambda: driver.find_element(By.ID, "btnLogin"),
            "find login button"
        )
        safe_click_element(driver, login_button, "login button")
        human_sleep(3.0, 5.0)  # Increased wait for post-login page load

        logging.info("Looking for action button")
        if action == "checkin":
            logging.info("Looking for clock-in button")
            button = safe_selenium_operation(
                lambda: wait.until(EC.element_to_be_clickable((By.ID, "cpContenidoCentral_lnkbtnGeneralInicio"))),
                "find clock-in button"
            )
        else:
            logging.info("Looking for clock-out button")
            button = safe_selenium_operation(
                lambda: wait.until(EC.element_to_be_clickable((By.ID, "cpContenidoCentral_lnkbtnGeneralFin"))),
                "find clock-out button"
            )

        logging.info("Clicking action button")
        safe_click_element(driver, button, f"{action} button")
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
