import os
import sqlite3
from datetime import datetime
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from chat_initiator import login_to_site, setup_chrome_options

LOGIN_URL = "https://azbyka.ru/znakomstva/login"
CHAT_URL = "https://chat.azbyka.ru/#481133"
# CHAT_URL = "https://chat.azbyka.ru/#485380"
CHAT_URL = "https://chat.azbyka.ru/#482721"
CHAT_URL = "https://chat.azbyka.ru/#470805"


# Загружаем данные из .env файла
load_dotenv()
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')


# Настройки браузера
options_chrome = setup_chrome_options()


def add_user_to_ignore(browser, profile_id):
    """
    Переходит на страницу профиля пользователя и кликает по ссылке "В игнор".

    Args:
        browser: Объект Selenium WebDriver.
        profile_id (int): ID профиля пользователя.
    """
    try:
        # Формируем URL профиля
        profile_url = f"https://azbyka.ru/znakomstva/profile/{profile_id}"

        # Открываем страницу профиля
        browser.get(profile_url)
        sleep(5)  # Ждем загрузки страницы

        # Ищем ссылку "В игнор" и кликаем по ней
        ignore_link = browser.find_element(By.LINK_TEXT, "В игнор")
        ignore_link.click()
        print(f"Пользователь {profile_id} добавлен в игнор.")
    except NoSuchElementException:
        print(f"Ссылка 'В игнор' для пользователя {profile_id} не найдена.")
    except Exception as e:
        print(f"Ошибка при добавлении пользователя {profile_id} в игнор: {str(e)}")

# Функция отправки сообщения
def send_message_and_check_ignore(browser, chat_url, message):
    try:
        # Открываем чат
        browser.get(chat_url)
        sleep(10)  # Ждем загрузки чата

        # Пробуем отправить сообщение
        message_input = browser.find_element(By.CSS_SELECTOR, ".real-input")
        message_input.send_keys(message, Keys.ENTER)
        print("Сообщение отправлено.")

        # Ждем и проверяем наличие сообщения об игноре
        sleep(5)
        if browser.find_element(By.ID, "info-box-content").text == "Сообщение не было отправлено, так как пользователь добавил Вас в игнор-лист.":
            print("Сообщение об игноре найдено")
            add_user_to_ignore(browser, 481133)
            return True
        print('Сообщения об игноре не найдено')
        return False

    except Exception as e:
        print("Ошибка:", str(e))


def check_message_read_status(browser, index, message_type=None):
    """
    Проверяет, прочитано ли сообщение по индексу в зависимости от его типа.

    Args:
        browser: Экземпляр веб-драйвера Selenium.
        index (int): Индекс сообщения для проверки.
        message_type (str, optional): Тип сообщения: "outcoming" или "incoming".

    Returns:
        bool: True, если сообщение прочитано, False, если непрочитано.
    """

    try:
        # Поиск контейнера с сообщениями
        sleep(10)
        messages = browser.find_elements(By.CSS_SELECTOR, "div.chat div.messages>div.message")
        # if not messages_container:
        #     raise NoSuchElementException("Контейнер с сообщениями не найден.")

        # messages = messages_container.find_elements(By.CLASS_NAME, "message")

        # Фильтрация сообщений по типу
        if message_type == "outcoming":
            messages = [msg for msg in messages if "outcoming" in msg.get_dom_attribute("class")]

        elif message_type == "incoming":
            messages = [msg for msg in messages if "incoming" in msg.get_dom_attribute("class")]
        else:
            messages = messages

        # Проверка индекса сообщения
        try:
            message = messages[index]
        except IndexError:
            print(f"Сообщение с индексом {index} не существует в данном чате.")

        # Проверяем наличие класса "unread"
        return "unread" not in message.get_dom_attribute("class").split()

    except NoSuchElementException as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Ошибка при проверке статуса сообщения: {e}")


def check_unanswered_messages(browser):
    sleep(5)
    try:
        messages = browser.find_elements(By.CSS_SELECTOR, "div.chat div.messages>div.message")
        message = messages[-1]
        if "incoming" in message.get_dom_attribute("class"):
            print('В чате {browser.current_url} есть неотвеченное сообщение')
            return browser.current_url
    except IndexError:
        print(f"Нет сообщений в чате по ссылке {browser.current_url}")

    except NoSuchElementException as e:
        print(f"Ошибка: {e} в чате {browser.current_url}")
    except Exception as e:
        print(f"Ошибка при проверке статуса сообщения: {e} в чате {browser.current_url}")


# Запуск браузера и выполнение сценария
with webdriver.Chrome(options=options_chrome) as browser:
    # Переходим на страницу авторизации
    browser.get(LOGIN_URL)
    login_to_site(browser, login, password)

    # Переходим в чат и выполняем проверку
    # print(send_message_and_check_ignore(browser, CHAT_URL, "."))
    # browser.get("https://chat.azbyka.ru/#470630")
    # print(check_message_read_status(browser, -1, message_type="outcoming"))

    browser.get(CHAT_URL)
    print(check_unanswered_messages(browser))
