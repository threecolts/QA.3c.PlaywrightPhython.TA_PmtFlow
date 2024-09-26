import os
import re

from playwright.sync_api import sync_playwright, expect
from pytest_playwright.pytest_playwright import playwright

from TA_Payment_Flow.tests.common_functions import unique_credentials, display_initial_page

def enter_cc_details(page):
    # Enter full name on card
    page.get_by_placeholder(" ", exact=True).fill("John Doe")

    



    iframe = page.frame_locator("iframe[name^='__privateStripeFrame']")
    iframe.locator("/html[1]/body[1]/div[6]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]").click()
    iframe.locator("/html[1]/body[1]/div[6]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]").fill("4242 4242 4242 4242")

    page.locator("iframe[name=\"__privateStripeFrame6364\"]").content_frame().get_by_label(
        "Credit or debit card number").fill("4242 4242 4242 4242")
    page.locator("iframe[name=\"__privateStripeFrame6366\"]").content_frame().get_by_label("ZIP").fill("12345")
    page.locator("iframe[name=\"__privateStripeFrame6365\"]").content_frame().get_by_label("Credit or debit card").fill(
        "11 / 33")
    page.locator("iframe[name=\"__privateStripeFrame6363\"]").content_frame().get_by_label(
        "Credit or debit card CVC/CVV").fill("123")


def ta_signup(pw1):
    # Convert the returned string to a boolean
    headless_mode = os.getenv("HEADLESS_MODE", "false").strip().lower() == "true"
    # test it in all 3 browsers
   # browser_types = ['chromium', 'firefox', 'webkit']
    # for browser_type in browser_types:
    email, fullname, userpass = unique_credentials()
    page, browser, context, stage_manager_url = display_initial_page(pw1, os.getenv("BROWSER"), headless_mode, 'ta_reg',500)
    page.get_by_role("textbox").fill(email)
    page.locator("button").filter(has_text="Continue with email").click()
    page.locator("#app input[name=\"full_name\"]").fill(fullname)
    page.locator("input[name=\"password\"]").fill(userpass)
    page.locator("input[name=\"confirm_password\"]").fill(userpass)
    # Click the Continue button
    page.get_by_label("tc-button").click()
    # CLick on Reseller or Retailer
    page.get_by_text("Arbitrage", exact=True).click()
    # Click on Seller Central (Amazon)
    page.get_by_text("Youtube").click()
    # Now click the Finish button
    page.locator("button").filter(has_text="Finish").click()
    """
    Manually log in to the DevTeam modal
    """
    # Enter name on pmt modal
    page.get_by_placeholder(" ", exact=True).fill("bill")
    """
    Having trouble with cc fields, skip for now
    """
    # Enter cc number
    # page.locator("iframe[name=\"__privateStripeFrame2754\"]").content_frame().get_by_label(
    #     "Card number").fill("4242 4242 4242 42422")

    # CLick on Enter a promo code
    page.get_by_text("Enter a promo code").click()
    # Make sure the Cancel button works
    page.locator("button").filter(has_text="Cancel").click()
    # enter an invalid promo code
    page.get_by_text("Enter a promo code").click()
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill("11111")
    # Click the Apply button
    page.locator("button").filter(has_text="Apply").click()
    # Verify the error message is displayed
    expect(page.get_by_role("tooltip")).to_contain_text("Sorry, this code isn't valid")
    # Now enter a valid code RRJ6POUG for 50% off



    # from this point, we test the Payment Details modal
    # Verify the modal is displayed
    try:
        expect(page.get_by_role("dialog")).to_contain_text("To activate your 7 day FREE trial")
    except AssertionError as e:
        print(f"An unexpected error occurred: {e}")
    # Enter cc Details
    enter_cc_details(page)


with sync_playwright() as pw:
    ta_signup(pw)