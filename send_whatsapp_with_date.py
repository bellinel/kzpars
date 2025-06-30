import os
import shutil
import requests
import asyncio
import zipfile

IDISTANSE = "" 
API_KEY = ""
CHAT_ID = ""

PATH_FOR_ARCHIVE ="" #'C:/Users/Admin/Desktop/Парсер штрафов/pdfs.zip'


async def create_zip_from_folder(folder_path, zip_name_without_ext):
    zip_path = f"{zip_name_without_ext}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    print(f"📦 Архив создан: {zip_path}")

    try:
        shutil.rmtree(folder_path)
        print(f"🗑️ Папка удалена: {folder_path}")
    except Exception as e:
        print(f"❌ Ошибка при удалении папки: {e}")

    return zip_path


async def send_file_whatsapp(zip_path):
    url = f"https://7105.api.greenapi.com/waInstance{IDISTANSE}/sendFileByUpload/{API_KEY}"
    
    payload = {
        'chatId': CHAT_ID,
        'fileName': 'штрафы_с_датой.zip'
    }

    try:
        with open(zip_path, 'rb') as f:
            files = [('file', ('штрафы_с_датой.zip', f, 'application/x-compressed'))]
            response = requests.post(url, data=payload, files=files)
            print(f"📤 Ответ от WhatsApp API: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при отправке файла: {e}")

    # Удаление архива после отправки
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"🗑 Архив удалён: {zip_path}")
    else:
        print(f"⚠️ Архив не найден для удаления: {zip_path}")


async def send_all_files_whatsapp():
    print('📦 Арихивация запущена')
    zip_path = await create_zip_from_folder('pdfs_with_date', PATH_FOR_ARCHIVE[:-4])
    await send_file_whatsapp(zip_path)






