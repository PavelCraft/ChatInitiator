import os
import sqlite3
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from chat_initiator import (login_to_site, setup_chrome_options,
                            update_user_data)

load_dotenv()
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')

LOGIN_URL = "https://azbyka.ru/znakomstva/login"

# Настройки браузера
options_chrome = setup_chrome_options()


def check_unanswered_messages(browser, user):
    profile_id = user['profile_id']  # Получаем profile_id один раз в начале
    browser.get(f"https://chat.azbyka.ru/#{profile_id}")
    name = user['name']
    sleep(5)
    try:
        profile_is_delete = browser.find_element(By.CLASS_NAME, "write-blocked")
        print('profile_is_delete =', profile_is_delete, 'profile_is_delete.text =', profile_is_delete.text)
        if profile_is_delete.text == "Анкета пользователя удалена.":
            print("Анкета пользователя удалена.")
            update_fields = {
                'profile_id': profile_id,
                'is_deleted': True
            }
            print('Вносим данные об удалении анкеты пользователя, вызывая функцию update_user_data из блока except функции sesd_messages')
            update_user_data(update_fields)
            return
    except Exception:
        pass

    try:
        messages = browser.find_elements(By.CSS_SELECTOR, "div.chat div.messages>div.message")
        message = messages[-1]
        if "incoming" in message.get_dom_attribute("class"):
            print(f'В чате с {name} по ссылке {browser.current_url} есть неотвеченное сообщение')
            return f"Имя: {name}, ссылка на чат: {browser.current_url}"
    except IndexError:
        print(f"Нет сообщений в чате по ссылке {browser.current_url}")

    except NoSuchElementException as e:
        print(f"Ошибка: {e} в чате {browser.current_url}")
    except Exception as e:
        print(f"Ошибка при проверке статуса сообщения: {e} в чате {browser.current_url}")



def get_profile_id_for_chat_links(db_name="user_profiles.db"):
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = '''
            SELECT profile_id, name
            FROM profiles
            WHERE is_deleted IS NOT TRUE
            AND is_ignoring IS NOT TRUE
            AND in_ignore IS NOT TRUE
        '''
        cursor.execute(query)
        records = cursor.fetchall()

    return [dict(record) for record in records]


# Список URL чатов
users = get_profile_id_for_chat_links()


def main():
    with webdriver.Chrome(options=options_chrome) as browser:
        browser.get(LOGIN_URL)
        login_to_site(browser, login, password)
        results = []
        for user in users:
            result = check_unanswered_messages(browser, user)
            if result:
                results.append(result)

    print("Результаты проверки чатов:")
    [print(result) for result in results]

main()