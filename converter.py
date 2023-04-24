import os
from dotenv import load_dotenv
from requests import request

path = os.path.join(os.path.dirname(__file__), '.env')  # получаем APP_ID и BOT_TOKEN из .env
if os.path.exists(path):
    load_dotenv(path)
    APP_ID = os.environ.get('APP_ID')
    BOT_TOKEN = os.environ.get('BOT_TOKEN')


def latest_rate():
    '''
    функция для отправления запроса и получения ответа о курсах валют
    '''
    response = request(
        method='GET',
        url='https://openexchangerates.org/api/latest.json',
        params={
            'app_id': APP_ID
        }
    )
    if response.status_code == 200:  # если всё успешно
        return {
            'USD': 1,
            **response.json()['rates']
        }
    return None