import psycopg2
import requests
from constants import COMPANIES_ID


def get_hh_data(companies_id: list[int] = COMPANIES_ID) -> list[dict]:
    """Получает данные по работодателям и их вакансиям с HH
       из списка companies_id, использует HeadHunterAPI"""
    hh_data = []
    base_request_url = 'https://api.hh.ru/'
    base_request_params = {'per_page': 100,
                           'page': 0}

    for company_id in companies_id:
        request_url = base_request_url + 'employers/' + str(company_id)
        company_data = requests.get(request_url).json()
        request_url = company_data['vacancies_url']

        request_params = base_request_params.copy()
        vacancies_data = []
        while True:
            responce = requests.get(request_url, params=request_params).json()
            request_params['page'] += 1
            vacancies_data.extend(responce['items'])
            if request_params['page'] >= responce['pages']:
                break

        hh_data.append({
            'company': company_data,
            'vacancies': vacancies_data
        })

    return hh_data


def is_db_exists(db_name: str, params: dict) -> bool:
    """Проверяет, есть ли БД с названием db_name"""
    conn = psycopg2.connect(dbname='postgres', **params)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname='%s'" % db_name)
        result = bool(cur.fetchone())
    conn.close()

    return result


def create_db(db_name: str, params: dict, sql_requests: dict) -> None:
    """Создает базу данных для работодателей и вакансий
       При наличии БД удаляет старые данные"""

    # Создаем базу
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute('DROP DATABASE IF EXISTS %s' % db_name)
    cur.execute('CREATE DATABASE %s' % db_name)

    conn.close()

    # Создаем таблицы.
    # Используем запрос из queries.sql под секцией [create_tables]
    conn = psycopg2.connect(dbname=db_name, **params)
    with conn.cursor() as cur:
        cur.execute(sql_requests['create_tables'])
    conn.commit()
    conn.close()


def put_data_to_db(hh_data: list[dict], db_name: str, params: dict, sql_requests: dict) -> None:
    """Заполняет БД данными, полученными с HH"""

    conn = psycopg2.connect(dbname=db_name, **params)
    with conn.cursor() as cur:
        for item in hh_data:
            company_id = int(item['company']['id'])
            # Заполняем данные по компании.
            # Используем запрос из queries.sql под секцией [put_data_in_table_companies]
            cur.execute(sql_requests['put_data_in_table_companies'],
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
                cur.execute(sql_requests['put_data_in_table_vacancies'],
                            (vacancy['id'],
                             company_id,
                             vacancy['name'],
                             salary_from,
                             salary_to,
                             salary_for_comparison,
                             vacancy['alternate_url']))

    conn.commit()
    conn.close()
