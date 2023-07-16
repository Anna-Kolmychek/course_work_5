-- [drop_db]
-- Удаление БД
DROP DATABASE IF EXISTS %s;

-- [create_db]
-- Создание БД
CREATE DATABASE %s;

-- [is_db_exists]
-- Проверка наличия БД
SELECT 1 FROM pg_database WHERE datname=%s;

-- [create_tables]
-- Создание таблиц для БД
CREATE TABLE companies(
    company_id int PRIMARY KEY,
    company_name varchar(50),
    company_url varchar(100)
);

CREATE TABLE vacancies(
    vacancy_id int PRIMARY KEY,
    company_id int REFERENCES companies ON DELETE CASCADE,
    vacancy_name varchar(100),
    salary_from int,
    salary_to int,
    salary_for_comparison int,
    vacancy_url varchar(100)
);


-- [put_data_in_table_companies]
-- Запись данных в таблицу companies
INSERT INTO companies (company_id, company_name, company_url) VALUES (%s, %s, %s);


-- [put_data_in_table_vacancies]
-- Запись данных в таблицу companies
INSERT INTO vacancies (vacancy_id,
                       company_id,
                       vacancy_name,
                       salary_from,
                       salary_to,
                       salary_for_comparison,
                       vacancy_url) VALUES (%s, %s, %s, %s, %s, %s, %s);

-- [get_companies_and_vacancies_count]
-- Получает список всех компаний и количество вакансий у каждой компании.
SELECT company_name, COUNT(*)
FROM companies
    JOIN vacancies USING(company_id)
GROUP BY company_id;


-- [get_all_vacancies]
-- Получает список всех вакансий с указанием названия компании,
-- названия вакансии, зарплаты и ссылки на вакансию."""
SELECT company_name, vacancy_name, salary_from, salary_to, vacancy_url
FROM companies
	JOIN vacancies USING(company_id);


-- [get_avg_salary]
-- Получает среднюю зарплату по вакансиям.
SELECT AVG(salary_for_comparison) FROM vacancies;


-- [get_vacancies_with_higher_salary]
-- Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
SELECT company_name, vacancy_name, salary_from, salary_to, vacancy_url
FROM companies
	JOIN vacancies USING(company_id)
WHERE salary_for_comparison > %s;


-- [get_vacancies_with_keyword]
-- Получает список всех вакансий, в названии которых содержатся переданные в метод слова,
-- например “python”.
SELECT company_name, vacancy_name, salary_from, salary_to, vacancy_url
FROM companies
	JOIN vacancies USING(company_id)
WHERE vacancy_name LIKE %s;