import os
import requests
import asyncio

IDISTANSE = "7105271174" 
API_KEY = "846ea21f0e6a4bd097b938f9956bdefb134268aad3344daab4"
CHAT_ID = "120363419948813756@g.us"


def save_files_whatsapp(file_name):
    url = f"https://7105.api.greenapi.com/waInstance{IDISTANSE}/uploadFile/{API_KEY}"

    files = [ 
        ('file', (file_name, open(f'pdf/{file_name}','rb'),'application/pdf')) 
    ]
    headers = {
        'Content-Type': 'application/pdf'
    }
    response = requests.post(url, files=files, headers=headers)
    url = response.text.encode('utf8')
    url = url.get('urlFile')
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
    for file in os.listdir('pdfs'):
        send_file_whatsapp(file)
        await asyncio.sleep(1)




