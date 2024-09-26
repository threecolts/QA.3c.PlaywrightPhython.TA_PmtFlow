"""
Contains common functions for tests
"""
import os
import random
import time

from dotenv import load_dotenv
load_dotenv()


def unique_credentials():
    mail_suffix = random.randint(10000000, 90000000)  # Generate a random 8-digit number
    user_email = f'wbarnes+{mail_suffix}@threecolts.com'
    full_name = f'wbarnes {mail_suffix}'
    user_pass = os.getenv("STAGE_MANAGER_TESTING_PW")
    return user_email, full_name, user_pass


def is_valid_in_xpath(pp, xpath):
    """
    If the word 'valid' is in the class attribute of the element located by the given XPath,
    the function returns True, indicating that the password has passed all validation checks.
    """
    # Wait for the element to be available in the DOM
    pp.wait_for_selector(xpath)

    # Check if the class attribute contains the word "valid"
    class_attribute = pp.locator(xpath).get_attribute("class") or ""
    return "valid" in class_attribute.split()


def display_initial_page(pw, browser_type='chromium', isheadless=True, initial_page_type='reg', delay=0):
    """
    Displays the Registration or Login page based on the initial page type that is passed in.
    """
    # Mapping of initial page types to environment variables
    env_var_mapping = {
        'reg': 'STAGE_MANAGER_REGISTRATION_URL',
        'login': 'STAGE_MANAGER_LOGIN_URL',
        'ta_reg': 'STAGE_MANAGER_TA_PAYMENT_FLOW_URL'
    }

    # Get the environment variable name and value
    env_var_name = env_var_mapping.get(initial_page_type)
    if not env_var_name:
        raise ValueError(f"Invalid initial page type: {initial_page_type}")

    stage_manager_url = os.getenv(env_var_name)
    if not stage_manager_url:
        raise ValueError(f"{env_var_name} is not defined")

    # Define the browser launcher functions in a dictionary
    browser_launchers = {
        'chromium': pw.chromium.launch,
        'firefox': pw.firefox.launch,
        'webkit': pw.webkit.launch
    }

    # Get the launch function for the specified browser type
    launch_browser = browser_launchers.get(browser_type)
    if not launch_browser:
        raise ValueError(f"Unsupported browser type: {browser_type}")

    # Launch the browser with specified options
    browser = launch_browser(headless=isheadless, slow_mo=delay)
    context = browser.new_context()
    page = context.new_page()
    page.goto(stage_manager_url)

    return page, browser, context, stage_manager_url


def login_to_manager(page, username, password):
    page.locator("#login-app input[type=\"text\"]").fill(username)
    page.locator("input[type=\"password\"]").fill(password)
    # Click the Continue button
    page.get_by_label("tc-button").nth(2).click()


def sign_out_of_manager(pg, username):
    # pg.get_by_role("button", name=username).click()
    pg.click("body > div:nth-child(1) > section:nth-child(1) > header:nth-child(1) > div:nth-child(1) > " \
             "div:nth-child(1) > div:nth-child(2) > button:nth-child(4) > span:nth-child(2)")
    pg.locator("a").filter(has_text="Sign Out").click()


def is_button_disabled(page, selector):
     return page.locator(selector).is_disabled()


def delay(milliseconds):
    # Convert milliseconds to seconds and pause the execution
    time.sleep(milliseconds / 1000.0)


def clear_specific_cookie(context, cookie_name):
    # Retrieve all cookies for the current context
    cookies = context.cookies()
    # Find the specific cookie to clear
    for cookie in cookies:
        if cookie['name'] == cookie_name:
            # Overwrite the specific cookie with an expired one
            context.add_cookies([{
                "name": "token_dev1",
                "value": "",  # Empty value to clear
                "domain": cookie['domain'],
                "path": cookie['path'],
                "expires": -1  # Expiry in the past
            }])
            # print(f"Cookie '{cookie_name}' has been cleared.")
            return
    raise Exception(f"{cookie_name} not found.")
