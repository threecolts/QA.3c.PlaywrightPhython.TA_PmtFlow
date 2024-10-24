import os
from playwright.sync_api import expect
import re


from promo_code_utils import display_the_promo_code_field


def get_toggle_status(page):
    toggle_button = page.locator('button[role="switch"]')
    is_checked = toggle_button.get_attribute('aria-checked')
    return 'Yearly' if is_checked == 'true' else 'Monthly'

def click_change_plan_if_visible(page):
    change_plan_button = page.locator("text='Change plan'")
    if change_plan_button.is_visible():
        change_plan_button.click()
    else:
        page.get_by_label("false").click()

def set_subscription_toggle(page, desired_selection):
    click_change_plan_if_visible(page)
    current_plan_type = get_toggle_status(page)
    if current_plan_type != desired_selection:
        page.get_by_role("switch").click()
    page.get_by_label("false").click()

def reset_plan_choice(page):
    click_change_plan_if_visible(page)
    page.locator("button").filter(has_text="Choose this plan").nth(0).click()


def select_and_verify_plan(page, plan_index, expected_price):
    page.locator("button").filter(has_text="Choose this plan").nth(plan_index).click()
    expect(page.get_by_role("dialog")).to_contain_text(f"${expected_price}")
    expect(page.get_by_role("dialog")).to_contain_text("$0.00")

# def select_and_verify_yearly_plan(page, plan_index, expected_price):

def verify_monthly_plans_no_discount(page):
    set_subscription_toggle(page, "Monthly")
    plans = [
        {"index": 0, "price": 129},
        {"index": 1, "price": 109},
        {"index": 2, "price": 69},
        {"index": 3, "price": 159},
        {"index": 4, "price": 59}
    ]
    for plan in plans:
        click_change_plan_if_visible(page)
        select_and_verify_plan(page, plan["index"], plan["price"])

    # Reselect the "Online Arbitrage" choice
    reset_plan_choice(page)

def verify_monthly_plans_fifty_percent_discount(page):
    # no need to flip the toggle to monthly, already there
    # set_subscription_toggle(page, "Monthly")
    plans = [
        {"index": 0, "price": 64.50},
        {"index": 1, "price": 54.50},
        {"index": 2, "price": 34.50},
        {"index": 3, "price": 79.50},
        {"index": 4, "price": 29.50}
    ]
    for plan in plans:
        click_change_plan_if_visible(page)
        select_and_verify_plan(page, plan["index"], plan["price"])

    # Reselect the "Online Arbitrage" choice
    reset_plan_choice(page)


def verify_yearly_plans_no_discount(page):
    set_subscription_toggle(page, "Yearly")

    # List of plans and expected prices
    plans = [
        {"index": 4, "price": "$590"},
        {"index": 4, "price": "$1,490"},
        {"index": 3, "price": "$690"},
        {"index": 2, "price": "$1,090"},
        {"index": 1, "price": "$1,290"},
        {"index": 0, "price": "$890"}
    ]

    for plan in plans:
        page.get_by_text("Change plan").click()
        page.locator("button").filter(has_text="Choose this plan").nth(plan["index"]).click()
        expect(page.get_by_role("dialog")).to_contain_text(plan["price"])
        expect(page.get_by_role("dialog")).to_contain_text("$0.00")

    # Reselect the "Online Arbitrage" choice
    reset_plan_choice(page)

def apply_20_percent_discount(page, promocode):
    # Apply a 20% promo code and verify it's applied correctly
    display_the_promo_code_field(page)
    page.locator("button").filter(has_text="Apply").click()
    expect(page.get_by_role("tooltip")).to_contain_text("20% discount applied")

