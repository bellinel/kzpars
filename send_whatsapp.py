import os
import requests
import asyncio
import zipfile

IDISTANSE = "7105271174" 
API_KEY = "846ea21f0e6a4bd097b938f9956bdefb134268aad3344daab4"
CHAT_ID = "120363419948813756@g.us"


def create_zip_from_folder(folder_path, zip_name):
    zip_path = f"{zip_name}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    print(f"📦 Архив создан: {zip_path}")
    return zip_path


def save_files_whatsapp(file_name):
    url = f"https://7105.api.greenapi.com/waInstance{IDISTANSE}/uploadFile/{API_KEY}"

    files = [ 
        ('file', (file_name, open(file_name,'rb'),'application/x-compressed')) 
    ]
    headers = {
        'Content-Type': 'application/x-compressed'
    }
    response = requests.post(url, files=files, headers=headers)
    json_data = response.json()
    url = json_data.get('urlFile')
    return url


def send_file_whatsapp(file_name):
    url = f"https://7105.api.greenapi.com/waInstance{IDISTANSE}/sendFileByUrl/{API_KEY}"

    payload = {
        'chatId': CHAT_ID,
        'url': save_files_whatsapp(file_name),
        'fileName': file_name
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


async def send_all_files_whatsapp():
    zip_path = create_zip_from_folder('pdfs', 'pdfs.zip')
    send_file_whatsapp(zip_path)
    




