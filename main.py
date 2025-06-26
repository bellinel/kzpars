from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import requests
import os
import urllib3

from chek_nca import find_nca

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_pdf(url):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"file_{timestamp}.pdf"

    response = requests.get(url, verify=False)
    with open(filename, 'wb') as f:
        f.write(response.content)


def check_auth(driver):
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'user-profile')]"))
        )
        print("✅ Авторизация успешна!")
        return True
    except:
        print("❌ Не удалось подтвердить авторизацию")
        return False



async def download_kz():    

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://erap-public.kgp.kz/#/login")



    select_lang = driver.find_element(By.XPATH, "/html/body/app-root/app-auth/div/div[2]/div[2]/app-lang/p-selectbutton/div/div[2]/span")
    select_lang.click()
    time.sleep(3)
            
    next_menu = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "span.icon-arrow-next"))
    )
    next_menu.click()
    # 2. Клик по кнопке ЭЦП (используем CSS-селектор для иконки)
    if check_auth(driver):

        # поиск контенера со штрафами
        while True:
            
            disabled_button = driver.find_element(
                    By.XPATH,
                    "//button[@disabled and .//span[text()='Следующие 10']]"
                )
                
            if disabled_button:
                print("❌ Нет штрафов")
                break
            

            try:
                dropdown_label = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "span.p-dropdown-label"))
                )
                dropdown_label.click()
                option = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//li[@role='option' and span[text()='Не оплачен']]"))
                )
                option.click()
                time.sleep(1)
                break
            except:
                print("❌ Не удалось найти комбобокс")
            try:
                button_next = driver.find_element(By.XPATH, "//button[not(@disabled) and .//span[text()='Следующие 10']]")
                container = driver.find_elements(By.XPATH, "//*[@id='pn_id_18-table']")
                for item in container:
                    tr = item.find_element(By.XPATH, "//*[@id='pn_id_18-table']/tbody/tr[1]")
                    button = tr.find_element(By.XPATH, "//*[@id='pn_id_18-table']/tbody/tr[1]/td[8]/div/button")
                    button.click()
                    time.sleep(1)
                

                    url_cont= WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='pn_id_41_content']/div/ul/li/a"))
                    )
                    
                    url = url_cont.find_element(By.XPATH, "//a[@target='_blank' and contains(@href, 'erap-public.kgp.kz')]")
                    url = url.get_attribute("href")

                    save_pdf(url)
                    driver.back()
                   
                button_next.click()
            except:
                break
                    
        
async def main():
    asyncio.create_task(find_nca())
    while True:
        await download_kz()
        time.sleep(10)



            

            
    # 3. Выбор Казтокен (NCALayer)
    
        


# if __name__ == "__main__":
#     asyncio.run(download_kz())


save_pdf()