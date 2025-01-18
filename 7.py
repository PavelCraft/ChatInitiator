import asyncio
import threading
import time

# Блокирующая функция
def check_unanswered_messages(browser, name):
    # Имитация выполнения блокирующей операции
    print(f"Старт check_unanswered_messages() для {name} в потоке c id {threading.current_thread().ident} в {time.strftime('%X')}")
    time.sleep(2)  # Имитация длительной операции
    print(f"Завершение check_unanswered_messages() для {name} в {time.strftime('%X')}")
    return f"Обработан чат: {name}"

# Функция для выполнения с ограничением на количество потоков
async def limited_check_unanswered_messages(semaphore, browser, name):
    async with semaphore:
        return await asyncio.to_thread(check_unanswered_messages, browser, name)

# Основная функция
async def main():
    print(f"Старт main в потоке c id {threading.current_thread().ident} в {time.strftime('%X')}")

    # Семафор для ограничения до 10 потоков
    semaphore = asyncio.Semaphore(10)

    # Список пользователей для обработки
    users = [f"Пользователь {i}" for i in range(1, 21)]  # 20 пользователей

    # Имитация браузера (можно заменить реальным объектом)
    browser = "DummyBrowser"

    # Создание задач с ограничением
    tasks = [limited_check_unanswered_messages(semaphore, browser, user) for user in users]

    # Ожидание завершения всех задач
    results = await asyncio.gather(*tasks)
    print("Результаты:")
    for result in results:
        print(result)

    print(f"Завершение main в {time.strftime('%X')}")

# Запуск
start = time.time()
asyncio.run(main())
print(f'Время выполнения программы: {(time.time() - start):.2f} секунд')
