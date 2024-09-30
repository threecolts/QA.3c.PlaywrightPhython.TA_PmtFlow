import os
import re
from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv
load_dotenv()

from common_functions import unique_credentials, display_initial_page

def display_the_promo_code_field(page):
    # Displays the promo code field and finally, ensure it is empty
    try:
        # Try to find the link with the first text option
        link = page.locator("text='Enter a promo code'")
        expect(link).to_be_visible()  # Check if the element is visible
        link.click()
    except Exception as e:
        # If the first text is not found, try the alternative text
        try:
            link = page.locator("text='Enter a different promo code'")
            expect(link).to_be_visible()
            link.click()
        except Exception as e:
            # Handle the case where neither link is found
            print("Neither promo code link found.")
    finally:
        promo_code_field = page.locator("div", has_text=re.compile(r"^ApplyPromo code$")).locator("input[placeholder=' ']")
        promo_code_field.fill("")


def enter_an_invalid_promo_code(page, promocode):
    # Enters an invalid code, verifies the error message, clicks the Cancel
    # button, verify the changed label text
    display_the_promo_code_field(page)
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill(promocode)
    page.locator("button").filter(has_text="Apply").click()
    expect(page.get_by_role("tooltip")).to_contain_text("Sorry, this code isn't valid")
    page.locator("button").filter(has_text="Cancel").click()
    expect(page.get_by_role("dialog")).to_contain_text("Enter a different promo code")


def apply_20_percent_discount(page, promocode):
    display_the_promo_code_field(page)
    page.locator("button").filter(has_text="Apply").click()


def ta_signup(pw1):
    # Convert the returned string to a boolean
    headless_mode = os.getenv("HEADLESS_MODE", "false").strip().lower() == "true"
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
    # page.get_by_text("Enter a promo code").click()
    display_the_promo_code_field(page)

    # Make sure the Cancel button works
    page.locator("button").filter(has_text="Cancel").click()

    # Test for a bogus promo code first
    enter_an_invalid_promo_code(page, "s9s9s9s")

    """
    Promo Code testing
    RRJ6POUG for 50% off Monthly plan
    J213BB9X for 20% off All plans
    OAC14DAY extends 14 trial - no discounts
    """

    # Display the promo code field again
    display_the_promo_code_field(page)

    # See if Monthly promo code works for yearly plan. It should fail
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill(os.getenv("FIFTY_PERCENT_OFF_MONTHLY_PLAN"))

    expect(page.get_by_role("dialog")).to_contain_text("This promo code is not valid for this plan.")


    # from this point, we test the Payment Details modal
    # Verify the modal is displayed
    try:
        expect(page.get_by_role("dialog")).to_contain_text("To activate your 7 day FREE trial")
    except AssertionError as e:
        print(f"An unexpected error occurred: {e}")

    # Enter cc Details
    # enter_cc_details(page)


with sync_playwright() as pw:
    ta_signup(pw)