-- [create_db]
-- Создание БД
DROP DATABASE IF EXISTS %s;
CREATE DATABASE %s;


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
                       vacancy_url) VALUES (%s, %s, %s, %s, %s, %s, %s)