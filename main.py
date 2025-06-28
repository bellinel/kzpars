from multiprocessing import Process
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
import os
import urllib3
from selenium.webdriver.common.action_chains import ActionChains

from chek_nca import find_nca
from send_whatsapp import send_all_files_whatsapp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def save_inn(inn):
    try:
        with open("inn.txt", "a", encoding="utf-8") as f:
            f.write(inn.strip() + "\n")
        print(f"📌 IIN сохранён: {inn}")
    except Exception as e:
        print(f"❌ Не удалось сохранить IIN: {inn} — {e}")

async def load_inn():
    try:
        with open("inn.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []


async def auth(driver):
    try:
        select_lang = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='radio' and @aria-label='РУ']"))
        )
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

def save_pdf(url, iin):
    folder = "pdfs"
    os.makedirs(folder, exist_ok=True)

    filename = os.path.join(folder, f"{iin}.pdf")

    response = requests.get(url, verify=False)
    with open(filename, 'wb') as f:
        f.write(response.content)

    print(f"📁 PDF сохранён как {filename}")

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
    driver.get("https://erap-public.kgp.kz/#/login")
    await auth(driver)

    if not check_auth(driver):
        return
    
    

    while True:
        await asyncio.sleep(1)
        

        try:
            tbody = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody.p-element.p-datatable-tbody'))
            )
        except:
            print("❌ Таблица не найдена")
            break

        try:
            rows = WebDriverWait(tbody, 10).until(
                EC.visibility_of_all_elements_located((By.TAG_NAME, "tr"))
            )
            print(f"🟢 Найдено {len(rows)} строк")

            iins_to_process = []
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if not cells:
                        continue

                    iin = ''.join(cells[0].text.strip().split())
                    status = cells[6].text.strip()

                    if status == "Не оплачен":
                        iins_to_process.append(iin)
                        print(f"📌 Обнаружен IIN: {iin} (Не оплачен)")
                except Exception as e:
                    print(f"⚠️ Ошибка при анализе строки: {e}")
                    continue

            if not iins_to_process:
                print("ℹ️ Нет необработанных записей на странице")
                break

            for iin in iins_to_process:
                if iin in await load_inn():
                    continue

                try:
                    # Получаем актуальный DOM перед каждым кликом
                    tbody = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody.p-element.p-datatable-tbody'))
                    )
                    rows = WebDriverWait(tbody, 10).until(
                        EC.visibility_of_all_elements_located((By.TAG_NAME, "tr"))
                    )

                    button = None
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells and cells[0].text.strip() == iin:
                            button = cells[7]
                            break

                    if not button:
                        continue
                    action = ActionChains(driver)
                    action.move_to_element(button).click().perform()
                    print(f"🟢 Открыл запись с IIN: {iin}")
                    await asyncio.sleep(1)

                    try:
                        protokol_li = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//li[p[contains(text(), 'Протокол')]]"))
                        )
                        pdf_link = protokol_li.find_element(By.TAG_NAME, "a")
                        href = pdf_link.get_attribute("href")
                        save_pdf(href, iin)
                        print(f"📥 PDF сохранён для {iin}")
                    except:
                        print(f"⚠️ PDF не найден для {iin}")

                    
                    await save_inn(iin)

                    driver.back()
                    await asyncio.sleep(1)

                    # Проверка на повторную авторизацию
                    try:
                        select_lang = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@role='radio' and @aria-label='РУ']"))
                        )
                        if select_lang:
                            select_lang.click()
                            await auth(driver)
                    except:
                        pass

                except Exception as e:
                    print(f"⚠️ Ошибка при обработке {iin}: {e}")
                    continue

            # Если все на этой странице уже обработаны — переходим дальше
            page_done = all(iin in await load_inn() for iin in iins_to_process)

            if page_done:
                try:
                    button_next = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Следующие 10']]"))
                    )

                    if button_next:
                        action = ActionChains(driver)
                        action.move_to_element(button_next).click().perform()
                        print("Эта страница отработана")
                        print("➡️ Переход на следующую страницу")
                        await asyncio.sleep(2)
                    
                except:
                    print("✅ Кнопка 'Следующие 10' не найдена")
                    break

        except Exception as e:
            print(f"❌ Ошибка в основном блоке: {e}")
            break

async def send_all_pdfs():
    print(f"📤 Отправка всех PDF-файлов запущена в {datetime.now()}")
    await send_all_files_whatsapp()
   

# --- Функция проверки времени и запуска отправки ---
async def check_time_and_run_send(target_time="09:00"):
    sent_today = False
    while True:
        now = datetime.now().strftime("%H:%M")
        
        if now == target_time and not sent_today:
            await send_all_pdfs()
            sent_today = True
            # Ждём минуту, чтобы не повторять в течение одной минуты
            await asyncio.sleep(60)
        elif now != target_time:
            sent_today = False
        await asyncio.sleep(1)


async def run_download_kz_loop():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    while True:
        await download_kz(driver)
        await asyncio.sleep(10)

async def run_check_time_loop():
    await check_time_and_run_send("09:00")



def start_download_process():
    asyncio.run(run_download_kz_loop())

def start_time_check_process():
    asyncio.run(run_check_time_loop())
        

if __name__ == '__main__':
    p1 = Process(target=start_download_process)
    p2 = Process(target=start_time_check_process)

    p1.start()
    p2.start()

    p1.join()
    p2.join()