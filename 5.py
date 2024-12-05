import os
import sqlite3
from datetime import datetime
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from chat_initiator import setup_chrome_options, login_to_site


LOGIN_URL = "https://azbyka.ru/znakomstva/login"

URL = "https://chat.azbyka.ru/#484508"



# Загружаем данные из .env файла
load_dotenv()
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')


options_chrome = setup_chrome_options()


# Запускаем браузер
with webdriver.Chrome(options=options_chrome) as browser:
    # Переходим на страницу авторизации
    browser.get(LOGIN_URL)
    login_to_site(browser, login, password)
    browser.get(URL)

    try:
        sleep(10)
        profile_is_delete = browser.find_element(By.CLASS_NAME, "write-blocked")
        print('profile_is_delete =', profile_is_delete)
        print('profile_is_delete.text =', profile_is_delete.text)
        if profile_is_delete.text == "Анкета пользователя удалена.":
            print("Анкета пользователя удалена.")
    except:
        print('Не удалось получить profile_is_delete или profile_is_delete.text')