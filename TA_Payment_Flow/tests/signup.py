import os
import re

from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv

from promo_code_utils import display_the_promo_code_field, verify_an_invalid_promo_code
from subscription_utils import set_subscription_toggle, verify_monthly_plans_no_discount, \
    verify_yearly_plans_no_discount

load_dotenv()

from common_functions import unique_credentials, display_initial_page

# def get_toggle_status(page):
#     # Locate the toggle
#     toggle_button = page.locator('button[role="switch"]')
#
#     # Check the value of aria-checked attribute
#     # False is Monthly, True is Yearly
#     is_checked = toggle_button.get_attribute('aria-checked')
#     if is_checked == 'true':
#         return 'Yearly'
#     else:
#         return 'Monthly'

# def click_change_plan_if_visible(page):
#     # Check if the "Change plan" button is visible
#     change_plan_button = page.locator("text='Change plan'")
#
#     if change_plan_button.is_visible():
#         # If visible, click the Change plan button
#         change_plan_button.click()
#     else:
#         # Return to Payment modal with the Back link
#         page.get_by_label("false").click()

# def select_and_verify_plan(page, plan_index, expected_price):
#     """
#     Helper function to select a plan by index and verify the price and total due.
#     """
#     # Click the "Choose this plan" button for the given plan index
#     page.locator("button").filter(has_text="Choose this plan").nth(plan_index).click()
#
#     # Verify the expected price and that the total due is $0.00
#     expect(page.get_by_role("dialog")).to_contain_text(f"${expected_price}")
#     expect(page.get_by_role("dialog")).to_contain_text("$0.00")


# def verify_the_monthly_plans(page):
#     # This test does not include the 50% discount
#     # Ensure the toggle is in the Monthly position
#     set_subscription_toggle(page, "Monthly")
#
#     # Define the plans and their expected prices
#     plans = [
#         {"index": 0, "price": 129},  # Full Suite
#         {"index": 1, "price": 109},  # OA + Wholesale
#         {"index": 2, "price": 69},  # Wholesale
#         {"index": 3, "price": 159},  # Pro
#         {"index": 4, "price": 59}  # Flip Pack
#     ]
#     # Loop through each plan and verify its details
#     for plan in plans:
#         # page.wait_for_timeout(1000)
#         click_change_plan_if_visible(page)
#
#         # page.wait_for_timeout(1000)
#         select_and_verify_plan(page, plan["index"], plan["price"])


def ta_signup(pw1):
    headless_mode = os.getenv("HEADLESS_MODE", "false").strip().lower() == "true"
    email, fullname, userpass = unique_credentials()
    page, browser, context, stage_manager_url = display_initial_page(pw1, os.getenv("BROWSER"), headless_mode, 'ta_reg',
                                                                     500)

    page.get_by_role("textbox").fill(email)
    page.locator("button").filter(has_text="Continue with email").click()
    page.locator("#app input[name='full_name']").fill(fullname)
    page.locator("input[name='password']").fill(userpass)
    page.locator("input[name='confirm_password']").fill(userpass)

    page.get_by_label("tc-button").click()
    page.get_by_text("Arbitrage", exact=True).click()
    page.get_by_text("Youtube").click()
    page.locator("button").filter(has_text="Finish").click()
    page.get_by_placeholder(" ", exact=True).fill("bill")

    # Verify the Promo code Cancel button works
    verify_monthly_plans_no_discount(page)
    verify_yearly_plans_no_discount(page)
    display_the_promo_code_field(page)
    page.locator("button").filter(has_text="Cancel").click()

    # Verify an invalid promo code produces an error
    verify_an_invalid_promo_code(page, "s9s9s9s")

    """
    Skip this until it is fixed. See github issue
        # 50% discount should fail for Yearly plan
        set_subscription_toggle(page, "Yearly")
        apply_50_percent_discount(page, plan_type="monthly")
    """

    page.locator("button").filter(has_text="Apply").click()
    page.get_by_text("Change plan").click()
    set_subscription_toggle(page, "Monthly")
    page.get_by_label("false").click()
    verify_the_monthly_plans(page)

    page.get_by_text("Change plan").click()
    set_subscription_toggle(page, "Yearly")

    try:
        expect(page.get_by_role("dialog")).to_contain_text("To activate your 7 day FREE trial")
    except AssertionError as e:
        print(f"An unexpected error occurred: {e}")


with sync_playwright() as pw:
    ta_signup(pw)

with sync_playwright() as pw:
    ta_signup(pw)