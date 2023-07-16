import psycopg2

from src.hh_api import get_hh_data
from config.constants import DB_NAME


class DBManager:
    def __init__(self, db_params: dict, sql_requests: dict, db_name: str = DB_NAME):
        """Инициализация экземпляра класса"""
        self.db_name = db_name
        self.db_params = db_params
        self.sql_requests = sql_requests
        if not self.is_db_exists():
            self.create_db()
            self.put_data_to_db()
        else:
            print('-' * 10, f'БД {self.db_name} уже существует', '-' * 10)


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
        result = {'avg_salary': int(db_data[0][0])}

        return result

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        salary_avg = self.get_avg_salary().get('avg_salary')
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

    def is_db_exists(self) -> bool:
        """Проверяет, есть ли такая БД"""
        conn = psycopg2.connect(dbname='postgres', **self.db_params)
        with conn.cursor() as cur:
            cur.execute(self.sql_requests['is_db_exists'], [self.db_name])
            result = bool(cur.fetchone())
        conn.close()

        return result

    def create_db(self) -> None:
        """Создает базу данных для работодателей и вакансий
           При наличии БД удаляет старые данные"""

        # Создаем базу
        # Используем запросы из queries.sql под секциями [drop_db], [create_db]
        conn = psycopg2.connect(dbname='postgres', **self.db_params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(self.sql_requests['drop_db'] % self.db_name)
        cur.execute(self.sql_requests['create_db'] % self.db_name)

        conn.close()

        # Создаем таблицы.
        # Используем запрос из queries.sql под секцией [create_tables]
        conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        with conn.cursor() as cur:
            cur.execute(self.sql_requests['create_tables'])
        conn.commit()
        conn.close()

        print('-' * 10, f'БД {self.db_name} создана', '-' * 10)

    def put_data_to_db(self) -> None:
        """Вызывает функцию получения данных с HH,
        заполняет БД полученными данными"""

        hh_data = get_hh_data()

        conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        with conn.cursor() as cur:
            for item in hh_data:
                company_id = int(item['company']['id'])
                # Заполняем данные по компании.
                # Используем запрос из queries.sql под секцией [put_data_in_table_companies]
                cur.execute(self.sql_requests['put_data_in_table_companies'],
                            (company_id,
                             item['company']['name'],
                             item['company']['alternate_url']))

                # Перебираем все вакансии компании
                for vacancy in item['vacancies']:
                    # Вычисляем рамки ЗП и среднюю ЗП для сравнения
                    salary_for_comparison = None
                    salary_from = None
                    salary_to = None
                    if vacancy.get('salary'):
                        salary = vacancy['salary']
                        if salary.get('from') and salary.get('to'):
                            salary_from = salary['from']
                            salary_to = salary['to']
                            salary_for_comparison = (salary_from + salary_to) / 2
                        elif not salary.get('from') and salary.get('to'):
                            salary_to = salary['to']
                            salary_for_comparison = salary_to
                        elif salary.get('from') and not salary.get('to'):
                            salary_from = salary['from']
                            salary_for_comparison = salary_from

                    # Заполняем данные по вакансии.
                    # Используем запрос из queries.sql под секцией [put_data_in_table_vacancies]
                    cur.execute(self.sql_requests['put_data_in_table_vacancies'],
                                (vacancy['id'],
                                 company_id,
                                 vacancy['name'],
                                 salary_from,
                                 salary_to,
                                 salary_for_comparison,
                                 vacancy['alternate_url']))

        conn.commit()
        conn.close()

        print('-' * 10, f'Данные с HeadHunter в БД {self.db_name} загружены', '-' * 10)
