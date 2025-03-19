import json
import os
import time
from playwright.sync_api import sync_playwright


LOGIN_URL = "https://hiring.idenhq.com/"
SESSION_FILE = "session.json"
USERNAME = "hananhamza94@gmail.com"
PASSWORD = "9xZ2uUZl"

def save_session(context):
    context.storage_state(path=SESSION_FILE)

def load_session(browser):
    if os.path.exists(SESSION_FILE):
        return browser.new_context(storage_state=SESSION_FILE)  
    return browser.new_context()



def login_and_save_session(page, context):
    print(" Logging in and saving session")
    page.goto(LOGIN_URL)
    page.get_by_role("textbox", name="Email").fill(USERNAME)
    page.get_by_role("textbox", name="Password").fill(PASSWORD)

    page.get_by_role("button", name="Sign in").click()
    page.wait_for_load_state("networkidle")
    save_session(context)
    print(" Session saved successfully!")

def launch_challenge(page):
    print("Scrolling to find Launch Challenge button")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)  
    print("Clicking Launch Challenge button")
    page.click("button:has-text('Launch Challenge')")
    page.wait_for_load_state("networkidle")
    print("Challenge page loaded")

def navigate_to_product_table(page):
    page.get_by_role("button", name="Menu").click()
    page.wait_for_timeout(1000)
    print(" Clicking Data Tools")
    page.click("text=Data Tools")
    page.wait_for_selector("text=Inventory Management")
    print(" Clicking Inventory Management")
    page.click("text=Inventory Management")
    page.wait_for_selector("text=Product Catalog")
    print(" Clicking Product Catalog")
    page.dblclick("text=Product Catalog")
   
    page.wait_for_load_state("networkidle")
    print(" Successfully navigated to Product Catalog!")

def fast_scroll_to_bottom(page):
    
    print(" Fast scrolling to the bottom...")

    previous_height = -1
    while True:
        
        page.evaluate("window.scrollBy(0, 3000)")
        page.wait_for_timeout(400)  

        
        current_height = page.evaluate("document.body.scrollHeight")

        if current_height == previous_height:
            print("Reached the bottom, all data should be loaded.")
            break  

        previous_height =current_height

def extract_all_product_cards(page):
    fast_scroll_to_bottom(page)
    print(" Extracting data from product cards")

    all_products = []
    
    cards = page.query_selector_all("div.grid > div")  

    print(f" Found {len(cards)} product cards.")

    for i, card in enumerate(cards):
        try:
            
            title_element = card.query_selector("div.h-12.flex.items-center.justify-center.font-medium.text-white")
            title = title_element.inner_text().strip() if title_element else "N/A"

           
            details = card.query_selector_all("div.flex.items-center.justify-between")
            product_data = {"Title": title}

            for detail in details:
                spans = detail.query_selector_all("span")
                if len(spans) == 2:
                    key = spans[0].inner_text().strip().replace(":", "")
                    value = spans[1].inner_text().strip()
                    product_data[key] = value

            all_products.append(product_data)
        

        except Exception as e:
            print(f" Error extracting product {i+1}: {e}")

    print(f" Extracted {len(all_products)} products.")
    return all_products


def save_to_json(data, filename="products.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f" Data saved to {filename}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  
        context = load_session(browser) 

        page = context.new_page()  
        html_content = page.content()
        print(html_content)  

        login_and_save_session(page, context)
        launch_challenge(page)
        navigate_to_product_table(page)
        product_data = extract_all_product_cards(page)
        save_to_json(product_data)

        browser.close()  


if __name__ == "__main__":
    main()
