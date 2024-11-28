import requests
from bs4 import BeautifulSoup
import json


# URL страницы
url = "https://azbyka.ru/znakomstva/member/userby-locations"  # замените на URL сайта

# Запрос страницы
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Найти тег <select> по его атрибуту (например, id или name)
select = soup.find('select', {'name': 'country'})  # замените field_name на нужное

# Извлечь значения из опций
options = [{"label": option.text, "value": option.get('value')} for option in select.find_all('option')]

# Сохранить в файл
with open("options.json", "w", encoding="utf-8") as f:
    json.dump(options, f, ensure_ascii=False, indent=4)

print("Значения сохранены в options.txt")
