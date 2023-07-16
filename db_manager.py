import json

import psycopg2

from config import config
from parser_sql import get_sql_requests


class DBManager:
    def __init__(self, db_name: str, db_params: dict, sql_requests: dict):
        """Инициализация экземпляра класса"""
        self.db_name = db_name
        self.db_params = db_params
        self.sql_requests = sql_requests

    def get_companies_and_vacancies_count(self) -> list[dict]:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        with conn.cursor() as cur:
            cur.execute(self.sql_requests['get_companies_and_vacancies_count'])
            db_data = cur.fetchall()
        conn.close()

        keys = ['company_name', 'vacancies_count']
        result = [dict(zip(keys, item)) for item in db_data]

        return result

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
           названия вакансии, зарплаты и ссылки на вакансию."""
        conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        with conn.cursor() as cur:
            cur.execute(self.sql_requests['get_all_vacancies'])
            db_data = cur.fetchall()
        conn.close()

        keys = ['company_name', 'vacancy_name', 'salary_from', 'salary_to', 'link']
        result = [dict(zip(keys, item)) for item in db_data]

        return result

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям."""
        conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        with conn.cursor() as cur:
            cur.execute(self.sql_requests['get_avg_salary'])
            db_data = cur.fetchall()
        conn.close()

        return int(db_data[0][0])

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        salary_avg = self.get_avg_salary()
        conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        with conn.cursor() as cur:
            cur.execute(self.sql_requests['get_vacancies_with_higher_salary'], [salary_avg])
            db_data = cur.fetchall()
        conn.close()

        keys = ['company_name', 'vacancy_name', 'salary_from', 'salary_to', 'link']
        result = [dict(zip(keys, item)) for item in db_data]

        return result

    def get_vacancies_with_keyword(self, key_word):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова,
        например “python”."""
        conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        key_word_in_query = f'%{key_word}%'
        with conn.cursor() as cur:
            cur.execute(self.sql_requests['get_vacancies_with_keyword'], [key_word_in_query])
            db_data = cur.fetchall()
        conn.close()

        keys = ['company_name', 'vacancy_name', 'salary_from', 'salary_to', 'link']
        result = [dict(zip(keys, item)) for item in db_data]

        return result

# db_name = 'test'
# sql_requests = get_sql_requests()
# db_params = config()
#
# db_manager = DBManager(db_name, db_params, sql_requests)
# res = db_manager.get_vacancies_with_keyword('Python')
# print(json.dumps(res, indent=2, ensure_ascii=False))
