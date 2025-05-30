"""
Система предотвращения атак типа "переполнение буфера".

В данном скрипте объединена следующая функциональность:
  - Конфигурация параметров (лимиты, регулярное выражение, настройка логирования).
  - Модуль фильтрации входных данных (проверка длины, обрезка пробелов).
  - Модуль валидации входных данных (проверка допустимых символов с помощью регулярных выражений).
  - Модуль логирования с ротацией файлов.
  - Основная логика обработки запроса.
  - Автоматизированное тестирование с использованием unittest.

Для запуска тестов выполните:
    python этот_файл.py unittest
    python этот_файл.py perfomancetest
Без аргументов запускается основное приложение.

"""

import os
import re
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import time
import random
import string

# ==========================
# CONFIGURATION SECTION
# ==========================
# Максимальная допустимая длина входной строки
MAX_INPUT_LENGTH = 25

# Регулярное выражение для допустимых символов:
# Разрешены латинские буквы, цифры, пробелы, дефисы и нижние подчеркивания.
VALID_PATTERN = r'^[A-Za-z0-9\s\-_]+$'

# Параметры логирования
LOG_DIR = "logs"
LOG_FILE_FORMAT = "log_%Y%m%d_%H%M%S.log"
MAX_LOG_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
BACKUP_COUNT = 5  # Количество резервных лог-файлов при ротации

# ==========================
# FILTERING MODULE
# ==========================

class Filter:
    @staticmethod
    def filter_input(data: str) -> str:
        """
        Фильтрует входные данные:
          - Проверяет, не превышает ли длина данных максимально допустимое значение.
          - Удаляет лишние пробелы с начала и конца строки.

        """
        if len(data) > MAX_INPUT_LENGTH:
            raise ValueError(f"Превышен допустимый объем входных данных ({MAX_INPUT_LENGTH} символов).")
        return data.strip()

# ==========================
# VALIDATOR MODULE
# ==========================

class Validator:
    @staticmethod
    def validate_input(data: str) -> str:
        """
        Валидирует входные данные с помощью регулярного выражения.

        """
        if not re.fullmatch(VALID_PATTERN, data):
            raise ValueError("Введенные данные содержат недопустимые символы.")
        return data

# ==========================
# LOGGING HANDLER MODULE
# ==========================

def setup_logging() -> None:
    """
    Настраивает систему логирования с ротацией файлов:
      - Создает каталог для логов, если он не существует;
      - Конфигурирует вывод логов в файл с ротацией и в консоль;
      - Выводит сообщение о запуске логирования и указывает путь к лог-файлу.

    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_filename = datetime.now().strftime(LOG_FILE_FORMAT)
    log_path = os.path.join(LOG_DIR, log_filename)
    
    # Настройка обработчика файлового логирования с ротацией
    file_handler = RotatingFileHandler(log_path, mode='a', maxBytes=MAX_LOG_FILE_SIZE,
                                       backupCount=BACKUP_COUNT, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
    file_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    # Настройка консольного вывода логов
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logging.info("Логирование запущено. Лог-файл: %s", log_path)

# ==========================
# MAIN FUNCTIONALITY
# ==========================

def process_request(user_input: str) -> str:
    """
    Обрабатывает входные данные:
      1. Пропускает строку через фильтрацию (проверка длины, обрезка пробелов).
      2. Валидирует отфильтрованную строку по заданному шаблону.
      3. При возникновении ошибки логирует её и возвращает пустую строку.

    """
    try:
        # Этап фильтрации
        filtered_data = Filter.filter_input(user_input)
        logging.info("Фильтрация успешна: '%s'", filtered_data)
        
        # Этап валидации
        validated_data = Validator.validate_input(filtered_data)
        logging.info("Валидация успешна: данные безопасны.")
        
        return validated_data
    except ValueError as error:
        logging.error("Ошибка обработки запроса: %s", error)
        return ""

def main():
    """
    Точка входа в программу.
      - Инициализирует логирование;
      - Принимает ввод от пользователя;
      - Обрабатывает введенные данные;
      - Выводит результаты в консоль.
    """
    setup_logging()
    logging.info("Система предотвращения атак типа 'переполнение буфера' запущена.")
    
    # Ввод данных от пользователя (в реальной системе данные могут поступать из сети или других источников)
    user_input = input("Введите данные: ")
    safe_data = process_request(user_input)
    
    if safe_data:
        print("Данные успешно обработаны:")
        print(safe_data)
    else:
        print("Ошибка обработки ввода. Проверьте логи для подробностей.")

# ==========================
# UNIT TESTS (USING unittest)
# ==========================

import unittest

class TestFilterAndValidator(unittest.TestCase):
    def test_filter_removes_extra_spaces(self):
        """Проверяет, что фильтр удаляет пробелы по краям строки."""
        input_data = "   Пример ввода   "
        expected_output = "Пример ввода"
        self.assertEqual(Filter.filter_input(input_data), expected_output)
    
    def test_filter_exceeds_max_length(self):
        """Проверяет, что при превышении максимальной длины выбрасывается исключение."""
        with self.assertRaises(ValueError):
            Filter.filter_input("A" * (MAX_INPUT_LENGTH + 1))
    
    def test_validator_allows_valid_input(self):
        """Проверяет, что корректный ввод проходит валидацию."""
        valid_input = "Valid_Input 123"
        self.assertEqual(Validator.validate_input(valid_input), valid_input)
    
    def test_validator_rejects_invalid_input(self):
        """Проверяет, что недопустимые символы приводят к исключению."""
        with self.assertRaises(ValueError):
            Validator.validate_input("Invalid@Input#!")

# ==========================
# PERFOMANCE TEST
# ==========================

class PerformanceTester:
    @staticmethod
    def generate_random_string(length):
        """Генерирует случайную строку заданной длины"""
        letters = string.ascii_letters + string.digits + " -_"
        return ''.join(random.choice(letters) for _ in range(length))

    @staticmethod
    def run_performance_test(num_requests=10000):
        """
        Запускает тест производительности с заданным количеством запросов.
        Измеряет общее время выполнения и запросов в секунду.
        Результаты записываются в лог-файл.
        """
        # Логируем начало теста
        logging.info("=== Начало теста производительности ===")
        logging.info("Количество запросов: %d", num_requests)

        # Генерируем тестовые данные (90% валидных, 10% невалидных)
        test_data = []
        for _ in range(num_requests):
            if random.random() < 0.9:  # 90% валидных данных
                length = random.randint(1, MAX_INPUT_LENGTH)
                test_data.append(PerformanceTester.generate_random_string(length))
            else:  # 10% невалидных данных
                length = random.randint(1, MAX_INPUT_LENGTH + 10)
                test_data.append(PerformanceTester.generate_random_string(length) + "!@#")

        start_time = time.perf_counter()

        # Обрабатываем все запросы
        success_count = 0
        failure_count = 0

        for data in test_data:
            try:
                filtered = Filter.filter_input(data)
                validated = Validator.validate_input(filtered)
                success_count += 1
            except ValueError as e:
                failure_count += 1
                # Логируем первые 5 ошибок для примера
                if failure_count <= 5:
                    logging.debug("Ошибка обработки: %s - %s", data, str(e))

        end_time = time.perf_counter()
        total_time = end_time - start_time
        requests_per_second = num_requests / total_time

        # Логируем результаты
        logging.info("=== Результаты теста производительности ===")
        logging.info("Общее время обработки: %.4f секунд", total_time)
        logging.info("Пропускная способность: %.2f запросов/секунду", requests_per_second)
        logging.info("Успешных запросов: %d (%.1f%%)", success_count, success_count / num_requests * 100)
        logging.info("Неудачных запросов: %d (%.1f%%)", failure_count, failure_count / num_requests * 100)
        logging.info("==========================================")

        # Также выводим результаты в консоль для удобства
        print("\n=== Результаты теста производительности ===")
        print(f"Результаты записаны в лог-файл")
        print(f"Общее время: {total_time:.4f} сек")
        print(f"Запросов/сек: {requests_per_second:.2f}")
        print(f"Успешно: {success_count} ({success_count / num_requests * 100:.1f}%)")
        print(f"Ошибок: {failure_count} ({failure_count / num_requests * 100:.1f}%)")

        return {
            "total_time": total_time,
            "requests_per_second": requests_per_second,
            "success_count": success_count,
            "failure_count": failure_count
        }

# ==========================
# SCRIPT EXECUTION CHOICE
# ==========================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "unittest":
            sys.argv.pop(1)
            unittest.main()
        elif sys.argv[1] == "performancetest":
            # Запускаем тест производительности
            setup_logging()
            logging.info("Запуск теста производительности...")

            # По умолчанию 10000 запросов
            num_requests = 10000

            # Если указан второй аргумент - используем его как количество запросов
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                num_requests = int(sys.argv[2])

            PerformanceTester.run_performance_test(num_requests)
        else:
            print("Использование:")
            print("  python этот_файл.py unittest           - запуск unit-тестов")
            print("  python этот_файл.py performancetest - запуск теста производительности")
            print("  python этот_файл.py                - запуск основного приложения")
    else:
        main()
