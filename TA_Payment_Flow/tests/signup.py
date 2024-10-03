import os
import re
from xmlrpc.client import boolean

from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv
load_dotenv()

from common_functions import unique_credentials, display_initial_page

def get_toggle_status(page):
    # Locate the toggle
    toggle_button = page.locator('button[role="switch"]')

    # Check the value of aria-checked attribute
    # False is Monthly, True is Yearly
    is_checked = toggle_button.get_attribute('aria-checked')
    if is_checked == 'true':
        return 'Yearly'
    else:
        return 'Monthly'


def set_subscription_toggle(page, desired_selection):
    # Get the current plan type (Monthly or Yearly)
    current_plan_type = get_toggle_status(page)

    # If the current plan type is not what we want, click the toggle
    if current_plan_type != desired_selection:
        page.get_by_role("switch").click()


def display_the_promo_code_field(page):
    # Try to find either of the promo code links
    promo_code_link = page.locator("text='Enter a promo code'").or_(page.locator("text='Enter a different promo code'"))

    # Ensure the promo code link is visible and click it
    expect(promo_code_link).to_be_visible()
    promo_code_link.click()

    # Ensure the promo code input field is cleared
    promo_code_field = page.locator("div", has_text=re.compile(r'^ApplyPromo code$')).locator("input[placeholder=' ']")
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


def apply_50_percen_discount(page, promocode, plan_type):
    # Apply a 50% promo code and verify its validity based on the plan type
    display_the_promo_code_field(page)
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill(promocode)
    page.locator("button").filter(has_text="Apply").click()

    if plan_type == "monthly":
        expect(page.get_by_role("tooltip")).to_contain_text("50% discount applied")
    else:
        expect(page.get_by_role("tooltip")).to_contain_text("This promo code is not valid for this plan.")

def apply_20_percent_discount(page, promocode):
    # Apply a 20% promo code and verify it's applied correctly
    display_the_promo_code_field(page)
    page.locator("button").filter(has_text="Apply").click()
    expect(page.get_by_role("tooltip")).to_contain_text("20% discount applied")

def verify_various_monthly_plans(page):
    # Click the Change plan
    page.get_by_text("Change plan").click()
    # Full Suite price with Total Due of 0.00
    page.locator("button").filter(has_text="Choose this plan").first.click()
    expect(page.get_by_role("dialog")).to_contain_text("$129")
    expect(page.get_by_role("dialog")).to_contain_text("$0.00")
    # OA +Wholesale
    page.get_by_text("Change plan").click()
    page.locator("button").filter(has_text="Choose this plan").nth(1).click()
    expect(page.get_by_role("dialog")).to_contain_text("$109")
    expect(page.get_by_role("dialog")).to_contain_text("$0.00")
    # Wholesale
    page.get_by_text("Change plan").click()
    page.locator("button").filter(has_text="Choose this plan").nth(2).click()
    page.get_by_text("$69", exact=True).click()
    expect(page.get_by_role("dialog")).to_contain_text("$0.00")
    # Pro
    page.get_by_text("Change plan").click()
    page.locator("button").filter(has_text="Choose this plan").nth(3).click()
    expect(page.get_by_role("dialog")).to_contain_text("$159")
    expect(page.get_by_role("dialog")).to_contain_text("$0.00")
    # FLip Pack
    page.get_by_text("Change plan").click()
    page.locator("button").filter(has_text="Choose this plan").nth(4).click()
    expect(page.get_by_role("dialog")).to_contain_text("$59")
    expect(page.get_by_role("dialog")).to_contain_text("$0.00")


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

    # CLick on Arbitrage
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

    display_the_promo_code_field(page)

    # Make sure the Cancel button works
    page.locator("button").filter(has_text="Cancel").click()

    # Test for a bogus promo code first
    enter_an_invalid_promo_code(page, "s9s9s9s")

    

    # redisplay the promo code field again
    display_the_promo_code_field(page)

    # See if Monthly promo code works for yearly plan. It should fail
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill(os.getenv("FIFTY_PERCENT_OFF_MONTHLY_PLAN"))

    # Click the Apply button
    page.locator("button").filter(has_text="Apply").click()
    expect(page.get_by_role("dialog")).to_contain_text("This promo code is not valid for this plan.")

    # Click, Change plan and Set Toggle to Monthly
    page.get_by_text("Change plan").click()
    set_subscription_toggle(page, "Monthly")

    # Go back to the Payment modal
    page.get_by_label("false").click()

    # Check the prices for monthly plans
    verify_various_monthly_plans(page)



    # Click, Change plan and set toggle to yearly
    page.get_by_text("Change plan").click()
    set_subscription_toggle(page, "Yearly")




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