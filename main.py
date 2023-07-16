import json

from config.config import config
from src.db_manager import DBManager
from src.parser_sql import get_sql_requests


def init_interaction() -> DBManager:
    """Начало взаимодействия с пользователем"""
    sql_requests = get_sql_requests()
    db_params = config()

    return DBManager(db_params, sql_requests)


def main(db_manager: DBManager):
    """Основная функция взаимодействия с пользователем"""
    while True:
        print("\nВыберите действие:\n"
              "0 – завершить работу\n"
              "1 – обновить данные с hh\n"
              "2 – вывести список всех компаний и количество вакансий у каждой компании\n"
              "3 – вывести список всех вакансий\n"
              "4 – вывести среднюю зарплату по вакансиям\n"
              "5 – вывести список всех вакансий, у которых зарплата выше средней по всем вакансиям\n"
              "6 – вывести список всех вакансий, в названии которых содержатся ключевое слово")
        user_action = input()

        try:
            user_action = int(user_action)
        except ValueError:
            print('-' * 10, 'Не корректный ввод данных', '-' * 10)
            continue

        if not (0 <= user_action <= 6):
            print('-' * 10, 'Не корректный ввод данных', '-' * 10)
            continue
        elif user_action == 0:
            exit()
        elif user_action == 1:
            db_manager.create_db()
            db_manager.put_data_to_db()
        elif user_action == 2:
            print(json.dumps(db_manager.get_companies_and_vacancies_count(),
                             indent=2, ensure_ascii=False))
        elif user_action == 3:
            print(json.dumps(db_manager.get_all_vacancies(),
                             indent=2, ensure_ascii=False))
        elif user_action == 4:
            print(json.dumps(db_manager.get_avg_salary(),
                             indent=2, ensure_ascii=False))
        elif user_action == 5:
            print(json.dumps(db_manager.get_vacancies_with_higher_salary(),
                             indent=2, ensure_ascii=False))
        elif user_action == 6:
            user_keyword = input('Введите ключевое слово: ')
            print(json.dumps(db_manager.get_vacancies_with_keyword(user_keyword),
                             indent=2, ensure_ascii=False))


if __name__ == '__main__':
    db_manager = init_interaction()
    main(db_manager)
