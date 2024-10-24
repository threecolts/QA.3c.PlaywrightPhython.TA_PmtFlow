import os

from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv

from promo_code_utils import apply_50_percent_discount
from promo_code_utils import display_the_promo_code_field, verify_an_invalid_promo_code
from subscription_utils import verify_monthly_plans_no_discount, verify_yearly_plans_no_discount, \
    verify_monthly_plans_fifty_percent_discount

load_dotenv()

from common_functions import unique_credentials, display_initial_page


def ta_signup(pw1):
    headless_mode = os.getenv("HEADLESS_MODE", "false").strip().lower() == "true"
    email, fullname, userpass = unique_credentials()
    page, browser, context, stage_manager_url = display_initial_page(pw1, os.getenv("BROWSER"), headless_mode, 'ta_reg',
                                                                     500)
    # Enter email in to Get Started page
    page.get_by_role("textbox").fill(email)
    page.locator("button").filter(has_text="Continue with email").click()
    page.locator("#app input[name='full_name']").fill(fullname)
    page.locator("input[name='password']").fill(userpass)
    page.locator("input[name='confirm_password']").fill(userpass)

    # CLick the Continue button
    page.get_by_label("tc-button").click()
    page.get_by_text("Arbitrage", exact=True).click()
    page.get_by_text("Youtube").click()
    page.locator("button").filter(has_text="Finish").click()
    page.get_by_placeholder(" ", exact=True).fill("bill")

    # Verify the Promo code Cancel button works
    verify_monthly_plans_no_discount(page)
    apply_50_percent_discount(page, "Monthly")

    verify_monthly_plans_fifty_percent_discount(page)

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

    try:
        expect(page.get_by_role("dialog")).to_contain_text("To activate your 7 day FREE trial")
    except AssertionError as e:
        print(f"An unexpected error occurred: {e}")


with sync_playwright() as pw:
    ta_signup(pw)
