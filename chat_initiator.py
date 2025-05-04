import os
import sqlite3
import sys
from datetime import datetime
from time import sleep

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from parameters import parameters

LOGIN_URL = 'https://azbyka.ru/znakomstva/login'
ADVANCED_SEARCH_URL = 'https://azbyka.ru/znakomstva/member/userby-locations'


if getattr(sys, 'frozen', False):  # Программа собрана
    base_path = sys._MEIPASS  # Путь ко временной директории PyInstaller
else:
    base_path = os.getcwd()  # Путь к текущей директории

dotenv_path = os.path.join(base_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')
db_name = os.getenv('DB_NAME')


def setup_chrome_options():
    "Функция для создания и настройки ChromeOptions"
    options_chrome = webdriver.ChromeOptions()
    # Игнорировать ошибки сертификатов
    options_chrome.add_argument('--ignore-certificate-errors')
    # Скрыть большинство логов
    options_chrome.add_argument('--log-level=3')
    # Дополнительная настройка для тишины
    options_chrome.add_argument('--silent')
    # Отключить логирование в Chrome
    options_chrome.add_argument('--disable-logging')
    return options_chrome


def setup_user_profile(options_chrome):
    "Функция для настройки профиля пользователя"
    options_chrome.add_argument(
        r'user-data-dir=C:\Users\Павел\AppData\Local\Google\Chrome\User Data'
    )
    options_chrome.add_argument(r'profile-directory=Profile 1')


def login_to_site(browser, login, password):
    "Функция для авторизации на сайте"
    browser.find_element(
        By.CSS_SELECTOR, "input[type='email']"
    ).send_keys(login)
    browser.find_element(
        By.CSS_SELECTOR, "input[type='password']"
    ).send_keys(password)
    browser.find_element(By.ID, 'submit').click()


def apply_filter_parameters(browser):
    "Вводит параметры фильтрации и получения списка анкет"
    # Переходим на страницу с фильтром
    browser.get('https://azbyka.ru/znakomstva/member/userby-locations')
    button = browser.find_element(By.NAME, 'advances_search')
    browser.execute_script('arguments[0].click();', button)
    button.click()
    browser.find_element(By.ID, 'proforma_search_link').click()

    # Вводим параметры фильтрации
    for key, value in parameters.items():
        select_element = browser.find_element(By.ID, key)
        select = Select(select_element)

        # Пытаемся выбрать нужное значение из выпадающего списка
        try:
            print('key =', key, 'value =', value)
            select.select_by_visible_text(value)
        except Exception:
            print(f'Для ключа {key} не удалось вставить значение')

    # Нажимаем кнопку 'Готово'
    browser.find_element(By.ID, 'done').click()


def get_user_profile_data(browser):
    user_data = []

    try:
        # Получаем количество пользователей
        text = browser.find_element(By.CLASS_NAME, 'fleft').text
        total_users_count = int(
            ''.join([symbol for symbol in text if symbol.isdigit()])
        )
        print('total_users_count =', total_users_count)
    except NoSuchElementException:
        # Если пользователей нет
        message = browser.find_element(
            By.CSS_SELECTOR, '.tip>span.warning'
        ).text
        print('Проблема:', message)
        return user_data

    def collect_user_data(browser):
        # Собираем ссылки на текущей странице
        sleep(10)
        page_user_links = [item.get_dom_attribute(
            'href') for item in browser.find_elements(
                By.CSS_SELECTOR, '.item_thumb_wrapper>a')]
        page_user_title = [item.get_dom_attribute(
            'title') for item in browser.find_elements(
                By.CSS_SELECTOR, '.item_thumb_wrapper>a')]
        ages = [title.split(', ')[0] for title in page_user_title if title]
        adresses = [
            ' '.join(title.split(', ')[1:]) for title
            in page_user_title if title
        ]
        page_user_names = [item.get_dom_attribute(
            'title') for item in browser.find_elements(
                By.CSS_SELECTOR, '.browsemembers_results_info>a')]
        print('Ссылки на пользователей:', page_user_links)
        print('Названия профилей:', page_user_title)
        print('Имена пользователей:', page_user_names)

        for link, name, age, adress in zip(
            page_user_links, page_user_names, ages, adresses
        ):
            user_data.append({
                'id': ''.join(
                    [symbol for symbol in link.split('/')[-1]
                     if symbol.isdigit()]),
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
        div_pages = browser.find_element(
            By.CLASS_NAME, 'paginationControl'
        )
        print('У нас есть блок с пагинацией')
        sleep(5)
        next_page_arrow = div_pages.find_element(
            By.CSS_SELECTOR, 'ul li:last-child a'
        )
        print(next_page_arrow)
        print('Удалось взять элемент-стрелочку в пагинации')

        while len(user_data) < total_users_count:
            # Проверяем, имеет ли кнопка класс 'selected'
            if (
                next_page_arrow.get_dom_attribute('class')
                and 'selected' in next_page_arrow.get_dom_attribute('class')
            ):
                print(
                    'Дошли до последний страницы поисковой выдачи, '
                    'прекращаем цикл'
                )
                break

            # Кликаем по кнопке перехода на следующую страницу
            browser.execute_script('arguments[0].click();', next_page_arrow)
            print('Кликаем на кнопку для перехода на следующую страницу')

            # Собираем ссылки на новой странице
            collect_user_data(browser)
            sleep(5)

            # Обновляем ссылки на элементы пагинации
            div_pages = browser.find_element(
                By.CLASS_NAME, 'paginationControl'
            )
            next_page_arrow = div_pages.find_element(
                By.CSS_SELECTOR, 'ul li:last-child a'
            )

    except NoSuchElementException:
        print('Получили одну страницу поисковой выдачи')

    # except Exception as error:
    #     print(error)

    finally:
        print(user_data)
        return user_data


def write_user_data_to_db(user_data, db_name=db_name):
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
                INSERT INTO profiles (
                           profile_id, name, age, date_added,
                           is_new_dialog, message_date, replied, address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile_id, name, age, current_date, None, None, None, address)
            )
        except sqlite3.IntegrityError:
            # Если запись с таким profile_id уже существует, пропускаем
            continue

    conn.commit()
    conn.close()

    print(f'Данные записаны в базу данных {db_name}')


def get_users_for_action(limit=10, db_name=db_name, action='send_message'):
    """
    Получает записи из базы данных для отправки сообщений или
    проверки ответов пользователей.

    Args:
        limit (int): Максимальное количество записей, которые нужно получить.
        db_name (str): Имя базы данных.
        action (str): Тип действия ('send_message' или 'check_replies').

    Returns:
        list: Список записей (словарей) с данными пользователей.
    """
    with sqlite3.connect(db_name) as conn:
        # Позволяет возвращать строки как словари
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if action == 'send_message':
            # Запрос для отправки сообщений: выбираем пользователей,
            # у которых поле is_new_dialog NULL
            query = '''
                SELECT profile_id, name
                FROM profiles
                WHERE is_new_dialog IS NULL
                AND is_deleted IS NOT TRUE
                AND is_ignoring IS NOT TRUE
                AND in_ignore IS NOT TRUE
                ORDER BY date_added DESC
                LIMIT ?
            '''
            cursor.execute(query, (limit,))
        elif action == 'check_replies':
            # Запрос для проверки ответов: выбираем пользователей с
            # is_new_dialog = 1 и replied IS NULL
            query = '''
                SELECT profile_id, message_date
                FROM profiles
                WHERE is_new_dialog = 1
                AND replied IS NULL
                AND is_deleted IS NOT TRUE
                AND is_ignoring IS NOT TRUE
                AND in_ignore IS NOT TRUE
            '''
            cursor.execute(query)
        else:
            raise ValueError(
                "Неверный параметр action. Должно быть 'send_message' "
                "или 'check_replies'."
            )

        records = cursor.fetchall()

    return [dict(record) for record in records]


def update_user_data(update_fields, db_name=db_name):
    """
    Обновляет данные в базе данных для определенных пользователей.

    Args:
        update_fields (dict): Словарь, где ключи — это имена столбцов
        для обновления, а значения — это новые значения для этих столбцов.
        db_name (str): Имя базы данных.

    Returns:
        None
    """
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Строим динамический SQL-запрос для обновления полей
    set_clause = ', '.join([f'{key} = ?' for key in update_fields.keys()])
    values = list(update_fields.values())

    try:
        cursor.execute(f'''
            UPDATE profiles
            SET {set_clause}
            WHERE profile_id = ?
        ''', values + [update_fields.get('profile_id')])

        conn.commit()
        updated_fields = ', '.join(
            [f'{key} = {repr(value)}' for key, value
             in update_fields.items()]
        )
        print(
            f'Данные для пользователя с profile_id = '
            f'{update_fields.get('profile_id')} были успешно обновлены: '
            f'{updated_fields}'
            )
    except sqlite3.Error as e:
        print(f'Ошибка при обновлении данных: {e}')
    finally:
        conn.close()


def check_ignore_message(browser):
    """
    Проверяет появление сообщения об игноре на странице.

    Args:
        browser: Объект Selenium WebDriver.

    Returns:
        bool: True, если сообщение об игноре найдено, иначе False.
    """
    try:
        # Ищем элемент с текстом сообщения
        ignore_message_text = browser.find_element(
            By.ID, 'info-box-content'
        ).text
        if ignore_message_text == (
            'Сообщение не было отправлено, так как пользователь '
            'добавил Вас в игнор-лист.'
        ):
            print('Сообщение об игноре найдено')
            return True
        return False
    except Exception as e:
        print('Ошибка при проверке игнора:', str(e))


def add_user_to_ignore(browser, profile_id):
    """
    Переходит на страницу профиля пользователя и кликает по ссылке 'В игнор'.

    Args:
        browser: Объект Selenium WebDriver.
        profile_id (int): ID профиля пользователя.

    Returns:
        bool: True, если пользователь успешно добавлен в игнор, иначе False.
    """
    try:
        # Формируем URL профиля
        profile_url = f'https://azbyka.ru/znakomstva/profile/{profile_id}'

        # Открываем страницу профиля
        browser.get(profile_url)
        sleep(5)  # Ждем загрузки страницы

        # Ищем ссылку 'В игнор' и кликаем по ней
        ignore_link = browser.find_element(By.LINK_TEXT, 'В игнор')
        ignore_link.click()
        print(f'Пользователь {profile_id} добавлен в игнор.')
        return True
    except NoSuchElementException:
        print(f"Ссылка 'В игнор' для пользователя {profile_id} не найдена.")
    except Exception as e:
        print(
            f'Ошибка при добавлении пользователя {profile_id} '
            f'в игнор: {str(e)}'
        )
    return False


def send_messages(browser, users):
    """
    Отправляет сообщения пользователям, если в чате меньше двух
    элементов с классом 'text'.

    Args:
        browser: Объект Selenium WebDriver.
        users (list): Список словарей с ключами 'id' и 'name'.

    Returns:
        int: Количество пользователей, которым сообщение не было отправлено.
    """
    not_sent_count = 0

    for user in users:
        # Получаем profile_id один раз в начале
        profile_id = user['profile_id']

        # Открываем страницу чата пользователя
        browser.get(f'https://chat.azbyka.ru/#{profile_id}')
        sleep(20)  # Ждём загрузки страницы

        try:
            # Проверяем количество элементов с классом 'text'
            text_elements = browser.find_elements(By.CLASS_NAME, 'text')
            if len(text_elements) > 1:
                # Если чат уже имеет сообщения, помечаем как не новый диалог
                update_fields = {
                    'profile_id': profile_id,
                    'is_new_dialog': False  # Помечаем как не новый диалог
                }
                print(
                    'Вносим данные о не новом диалоге, вызывая функцию '
                    'update_user_data из sesd_messages'
                )
                update_user_data(update_fields)

                not_sent_count += 1
                continue

            # Отправляем сообщение
            message = (f"Здравствуй, {user['name']}! Буду рад "
                       f"знакомству с тобой :ob")
            message_input = browser.find_element(
                By.CSS_SELECTOR, '.real-input'
            )
            message_input.send_keys(message, Keys.ENTER)
            sleep(100)  # Ждём 2 минуты перед началом следующего диалога

            if check_ignore_message(browser):
                update_fields = {
                    'profile_id': profile_id,
                    'is_ignored': True
                }
                if add_user_to_ignore(browser, profile_id):
                    update_fields['in_ignore'] = True
                print('Пользователь добавил в игнор. Вносим данные в базу.')
                update_user_data(update_fields)
                continue

            # Обновляем данные в базе данных после отправки сообщения
            update_fields = {
                'profile_id': profile_id,
                'message_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_new_dialog': True
            }
            print(
                'Вносим данные об отправке сообщения, вызывая функцию '
                'update_user_data из sesd_messages'
            )
            update_user_data(update_fields)

        except NoSuchElementException:
            print(f'Элемент не найден для пользователя {profile_id}.')
            try:
                profile_is_delete = browser.find_element(
                    By.CLASS_NAME, 'write-blocked'
                )
                print(
                    'profile_is_delete =', profile_is_delete,
                    'profile_is_delete.text =', profile_is_delete.text
                )
                if profile_is_delete.text == 'Анкета пользователя удалена.':
                    print('Анкета пользователя удалена.')
                    update_fields = {
                        'profile_id': profile_id,
                        'is_deleted': True
                    }
                    print(
                        'Вносим данные об удалении анкеты пользователя, '
                        'вызывая функцию update_user_data из блока '
                        'except функции sesd_messages'
                    )
                    update_user_data(update_fields)
            except Exception:
                print(
                    'Не удалось получить profile_is_delete или '
                    'profile_is_delete.text'
                )

    return not_sent_count


def check_message_read_status(browser, index, message_type=None):
    """
    Проверяет, прочитано ли сообщение по индексу в зависимости от его типа.

    Args:
        browser: Экземпляр веб-драйвера Selenium.
        index (int): Индекс сообщения для проверки.
        message_type (str, optional): Тип сообщения: 'outcoming'
        или 'incoming'.

    Returns:
        bool: True, если сообщение прочитано, False, если непрочитано.
    """

    try:
        # Поиск контейнера с сообщениями
        messages = browser.find_elements(
            By.CSS_SELECTOR, 'div.chat div.messages>div.message'
        )

        # Фильтрация сообщений по типу
        if message_type == 'outcoming':
            messages = [
                msg for msg in messages if 'outcoming'
                in msg.get_dom_attribute('class')
            ]

        elif message_type == 'incoming':
            messages = [
                msg for msg in messages if 'incoming'
                in msg.get_dom_attribute('class')
            ]
        else:
            messages = messages

        # Проверка индекса сообщения
        try:
            message = messages[index]
        except IndexError:
            print(f'Сообщение с индексом {index} не существует в '
                  f'чате по ссылке {browser.current_url}')

        # Проверяем наличие класса 'unread'
        print(
            f'Сообщение в чате {browser.current_url} прочитано:',
            'unread' not in message.get_dom_attribute('class').split()
        )
        return 'unread' not in message.get_dom_attribute('class').split()

    except NoSuchElementException as e:
        print(f'Ошибка: {e} в чате {browser.current_url}')
    except Exception as e:
        print(
            f'Ошибка при проверке статуса сообщения: {e} в '
            f'чате {browser.current_url}'
        )


def check_user_replied(browser):
    """
    Проверяет, ответил ли пользователь в чате, и обновляет поле
    replied в базе данных.

    Args:
        browser: Объект Selenium WebDriver.
        limit (int): Максимальное количество записей для проверки.
        db_name (str): Имя базы данных.

    Returns:
        None
    """
    users = get_users_for_action(action='check_replies')

    for user in users:
        profile_id = user['profile_id']
        message_date = datetime.strptime(
            user['message_date'], '%Y-%m-%d %H:%M:%S'
        )

        # Открываем страницу чата пользователя
        browser.get(f'https://chat.azbyka.ru/#{profile_id}')
        sleep(10)  # Ждем загрузки страницы

        text_elements = browser.find_elements(By.CLASS_NAME, 'text')
        print(profile_id, 'количество сообщений:', len(text_elements) - 1)
        status_first_message = check_message_read_status(browser, 0)

        if len(text_elements) >= 3:
            # Если сообщений с классом 'text' 3 или больше,
            # значит пользователь ответил
            update_fields = {
                'profile_id': profile_id,
                'replied': True,
                'unread': False
            }
            print(
                'Вносим данные об ответе, вызывая функцию '
                'update_user_data из check_user_replied'
            )
            update_user_data(update_fields)

        elif len(text_elements) < 3:
            # Если сообщений с классом 'text' меньше 3, проверяем,
            # прошло ли 14 дней
            days_diff = (datetime.now() - message_date).days
            if days_diff >= 7 and status_first_message:
                # Если прошло 7 дней, и сообщение прочитано,
                # ставим False в поле replied
                update_fields = {
                    'profile_id': profile_id,
                    'replied': False,
                    'unread': False
                }
                print(
                    'Вносим данные об отсутствии ответа в течение '
                    '7 дней, вызывая функцию update_user_data из '
                    'check_user_replied'
                )
                update_user_data(update_fields)


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
        sleep(5)

        # Находим список ссылок на анкеты из выдачи
        user_data = get_user_profile_data(browser)
        write_user_data_to_db(user_data)

        limit = 10

        while limit != 0:
            print('Цикл while в функции main, limit =', limit)
            users = get_users_for_action(limit)
            if not users:
                print(
                    'Пользователи из поисковой выдачи, с которыми не '
                    'начат диалог, закончились'
                )
                break
            limit = send_messages(browser, users)
            print(
                'После вычитания значения, которое вернула функция '
                'send_messages, limit стал равным', limit
            )

        print('Дошли до функции check_user_replied')
        check_user_replied(browser)
        sleep(30)


if __name__ == '__main__':
    user_profile = input('Будем использовать профайл вашего Chrome '
                         'с закладками и сессиями или нет? '
                         'Введите yes или no\n')
    if user_profile.lower() == 'yes':
        user_profile = True
    else:
        user_profile = False
    main(user_profile)
    sleep(30)
