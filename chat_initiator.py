from dotenv import load_dotenv
from time import sleep
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
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


def get_user_profile_links(browser):
    page_links = []
    user_links = []

    try:
        # Пытаемся найти блок с пагинацией
        div_pages = browser.find_element(By.CLASS_NAME, "paginationControl")

        pages = div_pages.find_elements(By.CSS_SELECTOR, "a[onclick]")

        # Получаем ссылки на все страницы
        for page in pages:
            browser.execute_script("arguments[0].click();", page)
            # Ожидаем, пока страница не загрузится
            browser.implicitly_wait(5)
            # После перехода на новую страницу находим все ссылки на пользователей
            page_user_links = [elem.get_attribute("href") for elem in browser.find_elements(By.CSS_SELECTOR, ".item_thumb_wrapper>a")]
            user_links.extend(page_user_links)
            page_links.append(browser.current_url)

    except NoSuchElementException:
        # Если пагинации нет, добавляем текущую страницу
        page_links.append(browser.current_url)
        print('Пагинация отсутствует, добавлена только текущая страница')

    print('page_links =', page_links)
    print('user_links =', user_links)

    return user_links


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
        apply_filter_parameters(browser)

        # Находим список ссылок на анкеты из выдачи
        get_user_profile_links(browser)
        sleep(30)

if __name__ == "__main__":
    user_profile = input("Будем использовать профайл вашего Chrome с закладками "
                         "и сессиями или нет? Введите yes или no\n")
    if user_profile.lower() == "yes":
        user_profile = True
    else:
        user_profile = False
    main(user_profile)
