import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time

#load environment variables
load_dotenv()
test_url = os.getenv("TEST_URL")

if not test_url:
    print("TEST_URL not found in environment variables. Please set it in your .env file.")
    exit(1)

# Setup driver
options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

companies = []

try:
    driver.get(test_url)
    wait = WebDriverWait(driver, 10)
    company_panels = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".euiPanel--paddingLarge")))

    for panel in company_panels:
        try:
            company_data={}
            name_block = panel.find_element(By.CSS_SELECTOR, ".euiLink")
            company_data["name"] = name_block.text.strip()
            company_data["company_link"] = name_block.get_attribute("href")

            avatars = panel.find_elements(By.CSS_SELECTOR, ".euiAvatar--user")
            contact_methods = {}

            for avatar in avatars:
                method = avatar.get_attribute("aria-label")
                # codul hexa #1fb3ab reprezinta ca exista acea metoda de contact
                bg_color = avatar.value_of_css_property("background-color")
                # hex #1fb3ab in rgb format (31,179,171)

                if(bg_color.startswith("rgba(")):
                    color_parts = bg_color.replace("rgba(", "").replace(")", "").split(",")
                    r = int(color_parts[0].strip())
                    g = int(color_parts[1].strip())
                    b = int(color_parts[2].strip())

                    is_existing_contact = (r == 31 and g == 179 and b == 171)
                else:
                    is_existing_contact = False

                contact_methods[method] = is_existing_contact


            company_data["contact_methods"] = contact_methods

            companies.append(company_data)
        except Exception as e:
            print(f"Error extracting a company panel: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    print("\nCompanies extracted:")
    for company in companies:
        print(f"Name: {company['name']}, Link: {company['company_link']}, Contact Methods: {company['contact_methods']}")
    print(f"Total companies extracted: {len(companies)}")

            

