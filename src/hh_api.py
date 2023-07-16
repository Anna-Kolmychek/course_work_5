import requests
from config.constants import COMPANIES_ID


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
