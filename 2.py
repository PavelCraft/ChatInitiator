from pywebio.input import input, input_group, select
from pywebio.output import put_text
import json

def save_settings():
    # Список значений для поля "Страна"
    with open("options.json", "r", encoding="utf-8") as f:
        countries = json.load(f)

    # Создание формы для ввода данных
    user_data = input_group("Настройки Chat Initiator", [
        input("Логин:", name="username", required=True),
        input("Пароль:", name="password", type="password", required=True),
        input("Ссылка на поисковую выдачу:", name="search_url", required=True),
        input("Сообщение для отправки:", name="message", required=True),
        select("Страна:", options=countries, name="country", required=True)
    ])

    # Сохранение данных в файл
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

    put_text("Настройки сохранены в файл settings.json.")

if __name__ == '__main__':
    from pywebio.platform import start_server
    start_server(save_settings, port=8080)
