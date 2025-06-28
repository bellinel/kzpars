import asyncio
import cv2
import pyautogui
import time
import numpy as np
import pyperclip


MY_PASSWORD = ""



def find_and_click(template_path, threshold=0.9):
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(template_path, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    if len(loc[0]) == 0:
        print(f"❌ Шаблон не найден: {template_path}")
        return False

    # Берем первую найденную позицию
    top_left = (loc[1][0], loc[0][0])
    center = (top_left[0] + w // 2, top_left[1] + h // 2)

    pyautogui.click(center)
    print(f"✅ Клик по: {template_path}, координаты: {center}")
    return True

# Пример последовательности:
 # время на открытие NCALayer вручную

async def auth_kz():
    i = 0
    while i < 10:
        if find_and_click('password_kz.png', 0.8):
            await asyncio.sleep(2)
            
            pyperclip.copy(MY_PASSWORD)
            await asyncio.sleep(0.5)
            pyautogui.rightClick()
            for i in range(5):
                 pyautogui.press('tab')
            pyautogui.press('enter')

        
            break
        
        i += 1
    i = 0
    while i < 10:
            if find_and_click('open_kz.png', 0.8):
                
                break
            
            i += 1
            if i > 10:
                print("❌ Не удалось найти кнопку open")
                break

    i = 0
    while i < 10:
            if find_and_click('select_kz.png'):
                find_and_click('approve_kz.png')   
                break
            
            i += 1
            if i > 10:
                print("❌ Не удалось найти кнопку select")
                break
            await asyncio.sleep(1)





async def auth():
    i = 0
    while i < 10:
        if find_and_click('password.png', 0.8):
            await asyncio.sleep(2)
            
            pyperclip.copy(MY_PASSWORD)
            await asyncio.sleep(0.5)
            pyautogui.rightClick()
            for i in range(5):
                 pyautogui.press('tab')
            pyautogui.press('enter')

        
            break
        
        i += 1
    i = 0
    while i < 10:
            if find_and_click('open.png', 0.8):
                
                break
            
            i += 1
            if i > 10:
                print("❌ Не удалось найти кнопку open")
                break

    i = 0
    while i < 10:
            if find_and_click('select.png'):
                find_and_click('approve.png')   
                break
            
            i += 1
            if i > 10:
                print("❌ Не удалось найти кнопку select")
                break
            await asyncio.sleep(1)
    

async def find_nca():
    print("🔍 Поиск NCALayer")
    while True:
        if find_and_click('start_kz.png'):
            await auth_kz()
            break
        if find_and_click('start.png'):
            await auth()
            break
        await asyncio.sleep(2)


