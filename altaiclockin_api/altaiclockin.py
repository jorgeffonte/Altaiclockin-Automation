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
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException

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
        login_button = driver.find_element(By.ID, "btnLogin")
        safe_click_element(driver, login_button, "login button")

        human_sleep(2.0, 4.0)

        logging.info("Looking for action button")
        if action == "checkin":
            button = driver.find_element(By.ID, "cpContenidoCentral_lnkbtnGeneralInicio")
        else:
            button = driver.find_element(By.ID, "cpContenidoCentral_lnkbtnGeneralFin")

        human_sleep(0.8, 2.0)
        logging.info("Clicking action button")
        safe_click_element(driver, button, f"{action} button")
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
