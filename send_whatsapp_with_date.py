import os

import shutil
import requests
import asyncio
import zipfile

IDISTANSE = "7105272703" 
API_KEY = "149b5d81cbf44f39a73cc57017320355a04b76a98dd945de89"

CHAT_ID = "120363418270288183@g.us"

PATH_FOR_ARCHIVE ='C:/Users/artur/OneDrive/Рабочий стол/projects/kz/pdfs_with_date.zip'


async def create_zip_from_folder(folder_path, zip_name_without_ext):
    if not os.path.exists(folder_path):
        print(f"❌ Папка не найдена: {folder_path}")
        return None

    zip_path = f"{zip_name_without_ext}.zip"

    # Если архив уже существует, предупреждаем и удаляем его
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
            print(f"🗑️ Старый архив удалён: {zip_path}")
        except Exception as e:
            print(f"❌ Не удалось удалить старый архив: {e}")
            return None

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
        'fileName': 'штрафы_с_датой'
    }

    try:
        f = open(zip_path, 'rb')
        files = [('file', ('pdfs_with_date.zip', f, 'application/octet-stream'))]
        response = requests.post(url, data=payload, files=files)
        print(f"📤 Ответ от WhatsApp API: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при отправке файла: {e}")
    finally:
        f.close()


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







