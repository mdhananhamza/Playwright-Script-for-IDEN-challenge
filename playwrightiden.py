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
    """Create a browser context, loading session if available."""
    if os.path.exists(SESSION_FILE):
        return browser.new_context(storage_state=SESSION_FILE)  
    return browser.new_context()



def login_and_save_session(page, context):
    print("🔹 Logging in and saving session...")
    page.goto(LOGIN_URL)
    page.get_by_role("textbox", name="Email").fill(USERNAME)
    page.get_by_role("textbox", name="Password").fill(PASSWORD)

    page.get_by_role("button", name="Sign in").click()
    page.wait_for_load_state("networkidle")
    save_session(context)
    print(" Session saved successfully!")

def launch_challenge(page):
    print("🔹 Scrolling to find 'Launch Challenge' button...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)  
    print("🔹 Clicking 'Launch Challenge' button...")
    page.click("button:has-text('Launch Challenge')")
    page.wait_for_load_state("networkidle")
    print("Challenge page loaded!")

def navigate_to_product_table(page):
    page.get_by_role("button", name="Menu").click()
    page.wait_for_timeout(1000)
    print("🔹 Clicking 'Data Tools'...")
    page.click("text=Data Tools")
    page.wait_for_selector("text=Inventory Management")
    print("🔹 Clicking 'Inventory Management'...")
    page.click("text=Inventory Management")
    page.wait_for_selector("text=Product Catalog")
    print("🔹 Clicking 'Product Catalog'...")
    page.dblclick("text=Product Catalog")
    ensure_page_fully_loaded(page)


    page.wait_for_load_state("networkidle")
    print(" Successfully navigated to Product Catalog!")


def ensure_page_fully_loaded(page):
    print("🔹 Scrolling to force content load...")
    
    prev_height = -1
    max_attempts = 10  
    
    for attempt in range(max_attempts):
        curr_height = page.evaluate("document.body.scrollHeight")

        if curr_height == prev_height:
            print("✅ Reached the bottom of the page.")
            break  
        
        page.evaluate("window.scrollBy(0, 1000)")
        page.wait_for_timeout(500)
        prev_height = curr_height  

    print("✅ Page fully loaded!")



def extract_all_table_data(page):
    ensure_page_fully_loaded(page)
  
    print(" Extracting data from all tables...")

    all_products = []
    tables = page.query_selector_all("table")  

    if not tables:
        print("No tables found on the page!")
        return []

    for table_index, table in enumerate(tables, start=1):
        print(f"Extracting data from Table {table_index}...")
        
        rows = table.query_selector_all("tbody tr")
        if not rows:
            print(f"No rows found in Table {table_index}, skipping...")
            continue

        for row_index, row in enumerate(rows, start=1):
            cells = row.query_selector_all("td")

            
            if len(cells) != 4:
                print(f" Skipping row {row_index} in Table {table_index} (Expected 4 cells, found {len(cells)})")
                continue  

            try:
                product = {
                    "table_index": table_index,
                    "row_index": row_index,
                    "ID": cells[0].inner_text().strip(),
                    "Material": cells[1].inner_text().strip(),
                    "Weight (kg)": cells[2].inner_text().strip(),
                    "Last Updated": cells[3].inner_text().strip(),
                }
                all_products.append(product)

            except Exception as e:
                print(f" Error extracting row {row_index} in Table {table_index}: {e}")

    print(f" Extracted {len(all_products)} products.")
    return all_products




def save_to_json(data, filename="products.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Data saved to {filename}")

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

        ensure_page_fully_loaded(page)


        product_data = extract_all_table_data(page)
        save_to_json(product_data)

        browser.close()  


if __name__ == "__main__":
    main()
