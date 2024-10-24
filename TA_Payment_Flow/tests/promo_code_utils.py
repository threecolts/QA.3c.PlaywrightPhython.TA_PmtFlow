import os

from playwright.sync_api import expect
from dotenv import load_dotenv
import re

load_dotenv()

def display_the_promo_code_field(page):
    # Display the Promo code field and ensures it is empty
    promo_code_link = page.locator("text='Enter a promo code'")
    if not promo_code_link.is_visible():
        promo_code_link = page.locator("text='Enter a different promo code'")
    expect(promo_code_link).to_be_visible()
    promo_code_link.click()
    promo_code_field = page.locator("div", has_text=re.compile(r'^ApplyPromo code$')).locator("input[placeholder=' ']")
    promo_code_field.fill("")

def verify_an_invalid_promo_code(page, promocode):
    display_the_promo_code_field(page)
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill(promocode)
    page.locator("button").filter(has_text="Apply").click()
    expect(page.get_by_role("tooltip")).to_contain_text("Sorry, this code isn't valid")
    page.locator("button").filter(has_text="Cancel").click()
    expect(page.get_by_role("dialog")).to_contain_text("Enter a different promo code")

def apply_monthly_fifty_percent_discount_code(page, promocode):
    display_the_promo_code_field(page)
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill(promocode)
    page.locator("button").filter(has_text="Apply").click()


def apply_50_percent_discount(page, plan_type):
    display_the_promo_code_field(page)
    page.locator("div").filter(has_text=re.compile(r"^ApplyPromo code$")).get_by_placeholder(" ").fill(os.getenv("FIFTY_PERCENT_OFF_MONTHLY_PLAN"))
    page.locator("button").filter(has_text="Apply").click()
    if plan_type == "Monthly":
        expect(page.get_by_role("dialog")).to_have_text(re.compile("Promo code applied: TA 50% Off on Monthly"))
    else:
        expect(page.get_by_role("tooltip")).to_contain_text("This promo code is not valid for this plan.")