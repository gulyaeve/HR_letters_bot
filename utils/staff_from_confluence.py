import datetime
import json
import logging
import re

from atlassian import Confluence

from config import Config
from bs4 import BeautifulSoup

from loader import staff
from utils.db_api.staff import Employee, Employees

months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']


def get_page_table_json():
    confluence = Confluence(
        url=Config.confluence_url,
        username=Config.confluence_login,
        password=Config.confluence_pass
    )
    page = confluence.get_page_by_id(
        page_id=Config.confluence_page_id,
        expand='body.storage'
    )
    page_content = page['body']['storage']['value']
    table_data = BeautifulSoup(page_content, features="html.parser").table
    table_list = [[cell.text for cell in row("td")]
                  for row in table_data("tr")]

    headers = table_list.pop(0)
    result = []
    for row in table_list:
        item = {}
        for index, title in enumerate(headers):
            item[title] = row[index]
        result.append(item)

    # write to file
    # with codecs.open("out.json", 'w', encoding='utf-8') as out:
    #     json.dump(result, out, ensure_ascii=False, indent=4)
    return json.dumps(result, ensure_ascii=False, indent=4)


def get_employees_from_confluence():
    staff = json.loads(get_page_table_json())
    all_employees = []
    for index, employee in enumerate(staff):
        person = Employee(
            id=index,
            telegram_id=None,
            lastname=employee['ФИО'].split()[0],
            firstname=employee['ФИО'].split()[1],
            middlename=employee['ФИО'].split()[2],
            phone=''.join(re.findall(r'\d+', employee['Мобильный']))[:11],
            email=employee['E-mail рабочий'].split("\xa0")[0],
            day_birth=int(employee['День рождения']) if employee['День рождения'] else None,
            month_birth=months.index(employee['Месяц рождения'].lower()) + 1 if employee['Месяц рождения'] in months else None,
        )
        all_employees.append(person)
    return Employees(all_employees)


async def make_sync():
    staff_from_db = await staff.select_all_employees()
    staff_from_page = get_employees_from_confluence()
    report = f"Отчёт по синхронизации таблицы confluence и базы бота от {datetime.datetime.now()}\n\n"
    emails_from_db = [employee_db.email.lower() for employee_db in staff_from_db]
    emails_from_page = [employee_page.email.lower() for employee_page in staff_from_page]
    for employee in staff_from_db:
        if employee.email.lower() not in emails_from_page:
            await staff.delete_employee(employee.id)
            logging.info(f"Removed employee {employee.full_name()} {employee.email}")
            report += f"УДАДЕН {employee.full_name()} {employee.email}\n"
    for employee in staff_from_page:
        if employee.email.lower() not in emails_from_db:
            await staff.add_employee(
                firstname=employee.firstname,
                lastname=employee.lastname,
                middlename=employee.middlename,
                phone=employee.phone,
                email=employee.email,
                day_birth=employee.day_birth,
                month_birth=employee.month_birth,
            )
            logging.info(f"Added employee {employee.full_name()} {employee.email}")
            report += f"ДОБАВЛЕН {employee.full_name()} {employee.email}\n"

    return report
