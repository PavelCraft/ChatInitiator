import time
from selenium import webdriver


def get_search_results():
    with webdriver.Chrome() as browser:
        browser.get('https://parsinger.ru/selenium/5.5/4/1.html')
        options_chrome = webdriver.ChromeOptions()
        options_chrome.add_argument("--log-level=3")
        time.sleep(5)


def start():
    login = input('Введите ваш логин от сайта знакомств: ')
    password = input('Введите ваш пароль от сайта знакомств: ')
    print(('Далее вам необходимо зайти на сайт знакомств, выбрать девушек по '
           'любым критериям (возраст, цель знакомства, город и т.д.), '
           'нажать кнопку "Искать", скопировать url поисковой выдачи'
           'и отправить его здесь')
           )
    search_results_url = input('Введите ссылку поисковой выдачи: ')


def main():
    start()

if __name__ == '__main__':
    main()