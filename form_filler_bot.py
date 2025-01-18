import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from chat_initiator import setup_chrome_options



URL_REGISTRATION = "http://127.0.0.1:8000/registracija/"
URL_FEEDBACK = "http://127.0.0.1:8000/feedback/"


options_chrome = setup_chrome_options()


# Запускаем браузер
with webdriver.Chrome(options=options_chrome) as browser:
    print('Выберите страницу для проверки:')
    print('1 - форма регистрации на субботний обед')
    print('2 - форма обратной связи')
    option = input('Введите цифру 1 или 2')
    # Переходим на страницу авторизации
    if option == 1:
        browser.get(URL_REGISTRATION)
    else:
        browser.get(URL_FEEDBACK)

    sleep(2)
    name = browser.find_element(By.ID, "id_name")
    name.send_keys('Bot')
    email = browser.find_element(By.ID, "id_email")
    email.send_keys('e@mail.ru')
    if option == 1:
        select_element = browser.find_element(By.ID, "id_portions")
        select = Select(select_element)
        select.select_by_visible_text("2")
    else:
        text = browser.find_element(By.ID, "id_text")
        text.send_keys('Что если сделать защиту от спам-роботов?')
    phone = browser.find_element(By.ID, "id_phone")
    print(phone)
    sleep(1)
    phone.send_keys('89859723780')

    # Нажимаем кнопку "Готово"
    button = browser.find_element(By.ID, "id_submit")
    browser.execute_script("arguments[0].click();", button)

    sleep(5)
