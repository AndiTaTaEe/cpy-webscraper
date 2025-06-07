from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = options)
web = "https://www.listafirme.ro/brasov/j{}.htm"

companies = []
page = 1

while True:
    driver.get(web.format(page))
    wait = WebDriverWait(driver, 10)
    rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.table tbody tr")))[1:]

    if not rows:
         break
    print(f"Scraping page number {page}")

    links_to_visit=[]
    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                number = cells[0].text.strip()
                company_bloc = cells[1]
                name = company_bloc.find_element(By.TAG_NAME, "a").text.strip()
                address = company_bloc.text.replace(name, '').strip()
                link_company = company_bloc.find_element(By.TAG_NAME, "a").get_attribute("href")

                contact_cell = cells[2]
                icons = contact_cell.find_elements(By.TAG_NAME, "i")
                contact_methods = [icon.get_attribute("title") for icon in icons if icon.get_attribute(("title"))]

                links_to_visit.append({
                    "Nr": number,
                    "Nume": name,
                    "Adresa": address,
                    "Link companie": link_company,
                    "Metode de contact": contact_methods
                })

        except Exception as e:
            print(f"Error processing row: {e}")

    for company_info in links_to_visit:
        try:
            driver.get(company_info["Link companie"])
            time.sleep(1.5)
            phone = "-"
            mobile = "-"
            email = "-"
            websites = []
            try:
                contact_table = driver.find_element(By.ID, "contact")
                rows_contact = contact_table.find_elements(By.TAG_NAME, "tr")
                for tr in rows_contact:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 2:
                        continue
                    label=tds[0].text.strip()
                    value=tds[1].text.strip()

                    if label=="Telefon":
                        phone=value.split(" ")[0]
                    elif label=="Mobil":
                        try:
                            mobile=value.split(" ")[0]
                        except:
                            mobile="-"
                    elif label=="Email":
                        try:
                            email=tds[1].find_element(By.TAG_NAME, "a").text.strip()
                        except:
                            email="-"
                    elif label=="Adresă web":
                        try:
                            company_site_links=tds[1].find_elements(By.TAG_NAME, "a")
                            websites = [a.get_attribute("href") for a in company_site_links]
                        except:
                            websites=[]
            except Exception as e:
                print(f"Contact table error: {e}")

            company_data={
                "Nr": company_info["number"],
                "Nume": company_info["name"],
                "Adresa": company_info["address"],
                "Contacte disponibile": company_info["contact_methods"],
                "Nr. telefon": phone,
                "Nr. mobil": mobile,
                "Email": email,
                "Site companie": websites,
                "Link Listafirme": company_info["link"]
                }

            companies.append(company_data)
        except Exception as e:
            print(f"Failed to extract data from {link_company}: {e}")

    page+=1

driver.quit()
for c in companies:
    print(c)