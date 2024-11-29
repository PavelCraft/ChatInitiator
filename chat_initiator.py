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

from parameters import parameters

LOGIN_URL = "https://azbyka.ru/znakomstva/login"
ADVANCED_SEARCH_URL = "https://azbyka.ru/znakomstva/member/userby-locations"


# Загружаем данные из .env файла
load_dotenv()
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')

# Функция для создания и настройки ChromeOptions
def setup_chrome_options():
    options_chrome = webdriver.ChromeOptions()
    options_chrome.add_argument("--ignore-certificate-errors")  # Игнорировать ошибки сертификатов
    options_chrome.add_argument("--log-level=3")  # Скрыть большинство логов
    options_chrome.add_argument("--silent")  # Дополнительная настройка для тишины
    options_chrome.add_argument("--disable-logging")  # Отключить логирование в Chrome
    return options_chrome

# Функция для настройки профиля пользователя
def setup_user_profile(options_chrome):
    options_chrome.add_argument(r"user-data-dir=C:\Users\Павел\AppData\Local\Google\Chrome\User Data")
    options_chrome.add_argument(r"profile-directory=Profile 1")

# Функция для авторизации на сайте
def login_to_site(browser, login, password):
    browser.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(login)
    browser.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
    browser.find_element(By.ID, "submit").click()

# Функция для ввода параметров фильтрации и получения списка анкет
def apply_filter_parameters(browser):
    # Переходим на страницу с фильтром
    browser.get("https://azbyka.ru/znakomstva/member/userby-locations")
    button = browser.find_element(By.NAME, "advances_search")
    browser.execute_script("arguments[0].click();", button)
    button.click()
    browser.find_element(By.ID, "proforma_search_link").click()

    # Вводим параметры фильтрации
    for key, value in parameters.items():
        select_element = browser.find_element(By.ID, key)
        select = Select(select_element)

        # Пытаемся выбрать нужное значение из выпадающего списка
        try:
            print('key =', key, 'value =', value)
            select.select_by_visible_text(value)
        except:
            print(f"Для ключа {key} не удалось вставить значение")

    # Нажимаем кнопку "Готово"
    browser.find_element(By.ID, "done").click()


def get_user_profile_data(browser):
    user_data = []

    try:
        # Получаем количество пользователей
        text = browser.find_element(By.CLASS_NAME, "fleft").text
        total_users_count = int(''.join([symbol for symbol in text if symbol.isdigit()]))
        print('total_users_count =', total_users_count)
    except NoSuchElementException:
        # Если пользователей нет
        message = browser.find_element(By.CSS_SELECTOR, ".tip>span.warning").text
        print("Проблема:", message)
        return user_data

    def collect_user_data(browser):
        # Собираем ссылки на текущей странице
        sleep(10)
        page_user_links = [item.get_dom_attribute(
            "href") for item in browser.find_elements(
                By.CSS_SELECTOR, ".item_thumb_wrapper>a")]
        page_user_title = [item.get_dom_attribute(
            "title") for item in browser.find_elements(
                By.CSS_SELECTOR, ".item_thumb_wrapper>a")]
        ages = [title.split(', ')[0] for title in page_user_title if title]
        adresses = [' '.join(title.split(', ')[1:]) for title in page_user_title if title]
        page_user_names = [item.get_dom_attribute(
            "title") for item in browser.find_elements(
                By.CSS_SELECTOR, ".browsemembers_results_info>a")]
        print("Ссылки на пользователей:", page_user_links)
        print("Названия профилей:", page_user_title)
        print("Имена пользователей:", page_user_names)


        for link, name, age, adress in zip(
            page_user_links, page_user_names, ages, adresses):
            user_data.append({
                'id': ''.join([symbol for symbol in link.split('/')[-1] if symbol.isdigit()]),
                'name': name,
                'adress': adress,
                'age': int(age.split()[0])
            })
        print('Удалось получить ссылки на профили на странице')

        print('Теперь количество ссылок в списке:', len(user_data))

    # Собираем ссылки с первой страницы
    collect_user_data(browser)

    try:
        # Ищем блок пагинации
        div_pages = browser.find_element(By.CLASS_NAME, "paginationControl")
        print('У нас есть блок с пагинацией')
        sleep(5)
        next_page_arrow = div_pages.find_element(By.CSS_SELECTOR, "ul li:last-child a")
        print(next_page_arrow)
        print('Удалось взять элемент-стрелочку в пагинации')

        while len(user_data) < total_users_count:
            # Проверяем, имеет ли кнопка класс "selected"
            if (next_page_arrow.get_dom_attribute("class")
                and "selected" in next_page_arrow.get_dom_attribute("class")):
                print('Дошли до последний страницы поисковой выдачи, прекращаем цикл')
                break

            # Кликаем по кнопке перехода на следующую страницу
            browser.execute_script("arguments[0].click();", next_page_arrow)
            print('Кликаем на кнопку для перехода на следующую страницу')


            # Собираем ссылки на новой странице
            collect_user_data(browser)
            sleep(5)

            # Обновляем ссылки на элементы пагинации
            div_pages = browser.find_element(By.CLASS_NAME, "paginationControl")
            next_page_arrow = div_pages.find_element(By.CSS_SELECTOR, "ul li:last-child a")

    except NoSuchElementException:
        print('Получили одну страницу поисковой выдачи')

    # except Exception as error:
    #     print(error)

    finally:
        print(user_data)
        return user_data


def write_user_data_to_db(user_data, db_name="user_profiles.db"):
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Проверяем, существует ли таблица, и создаём её, если нужно
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            profile_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            date_added TEXT NOT NULL,
            is_new_dialog BOOLEAN,
            message_date TEXT,
            replied BOOLEAN,
            address TEXT
        )
    ''')

    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Вставляем данные в таблицу
    for user in user_data:
        profile_id = user['id']
        name = user['name']
        age = user['age']
        address = user['adress']

        # Добавляем запись, если её ещё нет
        try:
            cursor.execute('''
                INSERT INTO profiles (profile_id, name, age, date_added, is_new_dialog, message_date, replied, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (profile_id, name, age, current_date, None, None, None, address))
        except sqlite3.IntegrityError:
            # Если запись с таким profile_id уже существует, пропускаем
            continue

    conn.commit()
    conn.close()

    print(f"Данные записаны в базу данных {db_name}")


def get_records_for_messaging(limit=10, db_name="user_profiles.db"):
    """
    Получает записи из базы данных для отправки сообщений.

    Args:
        limit (int): Максимальное количество записей, которые нужно получить.
        db_name (str): Имя базы данных.

    Returns:
        list: Список записей (словарей) с данными пользователей.
    """
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row  # Позволяет возвращать строки как словари
        cursor = conn.cursor()
        cursor.execute('''
            SELECT profile_id, name
            FROM profiles
            WHERE is_new_dialog IS NULL
            ORDER BY date_added DESC
            LIMIT ?
        ''', (limit,))
        records = cursor.fetchall()

    return [dict(record) for record in records]


def send_messages(browser, users):
    """
    Отправляет сообщения пользователям, если в чате меньше двух элементов с классом 'text'.

    Args:
        browser: Объект Selenium WebDriver.
        users (list): Список словарей с ключами 'id' и 'name'.

    Returns:
        int: Количество пользователей, которым сообщение не было отправлено.
    """
    not_sent_count = 0

    for user in users:
        # Открываем страницу чата пользователя
        browser.get(f"https://chat.azbyka.ru/#{user['profile_id']}")
        sleep(20)  # Ждём загрузки страницы

        try:
            # Проверяем количество элементов с классом "text"
            text_elements = browser.find_elements(By.CLASS_NAME, "text")
            if len(text_elements) > 1:
                not_sent_count += 1
                continue

            # Отправляем сообщение
            message = f"Здравствуй, {user['name']}! Буду рад знакомству с тобой :ob"
            message_input = browser.find_element(By.CSS_SELECTOR, ".real-input")
            message_input.send_keys(message, Keys.ENTER)
            sleep(100)  # Ждём 2 минуты перед началом следующего диалога

        except NoSuchElementException:
            print(f"Элемент не найден для пользователя {user['id']}.")

    return not_sent_count


def main(user_profile):
    options_chrome = setup_chrome_options()
    if user_profile:
        setup_user_profile(options_chrome)

    # Запускаем браузер
    with webdriver.Chrome(options=options_chrome) as browser:
        # Переходим на страницу авторизации
        browser.get(LOGIN_URL)

        # Выполняем авторизацию
        if not user_profile:
            login_to_site(browser, login, password)


        # Применяем фильтрацию
        # apply_filter_parameters(browser)
        # sleep(5)

        # # Находим список ссылок на анкеты из выдачи
        # user_data = get_user_profile_data(browser)
        # write_user_data_to_db(user_data)

        limit = 10

        while limit != 0:
            users = get_records_for_messaging(limit)
            limit -= send_messages(browser, users)
        sleep(30)

if __name__ == "__main__":
    user_profile = input("Будем использовать профайл вашего Chrome с закладками "
                         "и сессиями или нет? Введите yes или no\n")
    if user_profile.lower() == "yes":
        user_profile = True
    else:
        user_profile = False
    main(user_profile)
