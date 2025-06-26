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

async def auth(driver):
    try:
        select_lang = driver.find_element(By.XPATH, "/html/body/app-root/app-auth/div/div[2]/div[2]/app-lang/p-selectbutton/div/div[2]/span")
        select_lang.click()
        await asyncio.sleep(3)
            
        next_menu = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.icon-arrow-next"))
        )
        next_menu.click()

        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Выбрать сертификат')]")
        button.click()
        await find_nca()
    except:
        print("❌ Не удалось авторизоваться")
        



def save_pdf(url):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"file_{timestamp}.pdf"

    response = requests.get(url, verify=False)
    with open(filename, 'wb') as f:
        f.write(response.content)


def check_auth(driver):
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(@class, 'username')]"))
        )
        print("✅ Авторизация успешна!")
        return True
    except:
        print("❌ Не удалось подтвердить авторизацию")
        return False



async def download_kz(driver):    

    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://erap-public.kgp.kz/#/login")

    await auth(driver)
    chek_auth = check_auth(driver)

    # 2. Клик по кнопке ЭЦП (используем CSS-селектор для иконки)
    
    if chek_auth:
        processed_iins = set()
        while True:
            try:
                await asyncio.sleep(1)

        # Получаем обновлённый список строк
                container = driver.find_elements(By.XPATH, "//table[@id='pn_id_18-table']//tbody/tr")

                for i, item in enumerate(container):
                    try:
                        cells = item.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 8:
                            iin = cells[2].text.strip()
                            status = cells[6].text.strip()

                            # Пропускаем, если уже обрабатывали или статус не "Не оплачен"
                            if iin in processed_iins or status != "Не оплачен":
                                continue

                            processed_iins.add(iin)  # Отмечаем как обработанный

                            # Кликаем на кнопку
                            button = cells[7].find_element(By.TAG_NAME, "button")
                            driver.execute_script("arguments[0].click();", button)
                            print(f"🟢 Открыл запись с ИИН: {iin}")
                            await asyncio.sleep(1)

                            # Обрабатываем PDF
                            try:
                                protokol_li = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.XPATH, "//li[p[contains(text(), 'Протокол')]]"))
                                )
                                # Находим ссылку внутри
                                pdf_link = protokol_li.find_element(By.TAG_NAME, "a")
                                href = pdf_link.get_attribute("href")
                                save_pdf(href)
                                print("📥 PDF сохранён")
                                driver.back()
                                await asyncio.sleep(1)
                                await auth(driver)
                                
# После возврата назад — ждём, пока снова загрузится таблица
                                WebDriverWait(driver, 15).until(
                                    EC.presence_of_element_located((By.XPATH, "//table[@id='pn_id_18-table']//tbody/tr"))
                                )
                                # Продолжаем цикл — без break
                                continue

                            except:
                                print("⚠️ PDF не найден")

                            # Назад к таблице
                            

                             # После одной записи — перезапускаем цикл и обновляем container

                    except Exception as e:
                        print(f"⚠️ Ошибка в записи {i}: {e}")

                # Переход к следующей странице
                    try:
                        button_next = driver.find_element(By.XPATH, "//button[.//span[text()='Следующие 10']]")
                        if button_next.is_enabled():
                            button_next.click()
                            print("➡️ Переход на следующую страницу")
                            await asyncio.sleep(3)
                        else:
                            print("✅ Последняя страница достигнута")
                            break
                    except:
                        print("✅ Кнопка 'Следующие 10' не найдена")
                        break

            except Exception as e:
                print(f"❌ Ошибка в основном цикле: {e}")
                break


        



                    
        
async def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    while True:
        await download_kz(driver)
        await asyncio.sleep(10)




            

            
    # 3. Выбор Казтокен (NCALayer)
    
        


if __name__ == "__main__":
    asyncio.run(main())


