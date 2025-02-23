import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

def product_search(image_path, headless=True):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if headless: 
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    results = []
    
    try:
        driver.get("https://images.google.com/")

        lens_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "Gdd5U"))
        )
        lens_button.click()

        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        upload_input.send_keys(image_path)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        time.sleep(3)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        collected_items = 0
        spans = soup.find_all("span", class_="EwVMFc")
        
        for span in spans:
            if collected_items >= 5:
                break
            
            next_link = span.find_next("a", href=True)
            if next_link and next_link["href"].startswith("http"):
                price = span.get_text(strip=True)[:-1]
                href = next_link["href"]
                img = span.parent.parent.parent.find('img')['src']
                results.append({"price": price, "link": href, "img": img})
                collected_items += 1
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()
    
    return results

if __name__ == "__main__":
    print("Reverse Image Search")
    image_path = "/Users/isaac/programming/hacklytics25/src/test_data/img-1.png"
    results = product_search(image_path, False)
    print(results)