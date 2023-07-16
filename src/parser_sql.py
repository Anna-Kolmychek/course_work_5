import re

from config.constants import SQL_FILE_NAME


def get_sql_requests(sql_file_name: str = SQL_FILE_NAME) -> dict:
    """Парсер файла .sql
       Получает словарь из запросов SQL для разных функций и методов"""
    sql_requests = {}
    sql_request = ''
    sql_request_key = ''
    with open(sql_file_name, 'r', encoding='utf-8') as sql_file:
        for line in sql_file:
            if re.search('\[.*]', line):
                if sql_request_key:
                    sql_requests[sql_request_key] = sql_request
                sql_request_key = re.search('\[.*]', line)[0][1:-1]
                sql_request = ''
            sql_request += line

        if sql_request_key:
            sql_requests[sql_request_key] = sql_request

    return sql_requests
