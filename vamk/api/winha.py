# -*- coding: utf-8 -*-
"""
    vamk.api.winha
    ~~~~~~~~~~~~~~
    Implements winha crawler.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import bs4
import re
from crawler import Crawler


class Winha(Crawler):
    """Inherits Crawler class. Simulates the browser to login in to the Winha student system, in order to get the desired data based on the
    HTML documents. The desired data in this case are student information, courses, and gpa & grades distribution
    (based on courses).
    """

    # Collecting all of the URLs needed.
    URLS = {
        'ELOGON_URL': 'https://secure.puv.fi/wille/elogon.asp',
        'LOGIN_URL': 'https://secure.puv.fi/wille/elogon.asp?dfUsername?dfPassword?dfUsernameHuoltaja',
        'EMAINVAL_URL': 'https://secure.puv.fi/wille/emainval.asp',
        'EHOPSSIS_URL': 'https://secure.puv.fi/wille/ehopssis.asp',
        'EHOPSSIS_KAIKKI_URL': 'https://secure.puv.fi/wille/ehopssis.asp?Opinto=Kaikki&ID=0',
        'EHENKILO_URL': 'https://secure.puv.fi/wille/eHenkilo.asp'
    }

    def __init__(self, student_id, password):
        """Constructor for getting student id and password.
        """

        # Initializing the base class Crawler.
        Crawler.__init__(self)

        self.student_id = student_id
        self.password = password

        # Structuring the authentication data into a dict for posting to the server.
        self.auth_data = {'dfUsernameHidden': student_id,
                          'dfPasswordHidden': password}

        # Login the website then other requests can be made with this session and getting the status of login.
        self.status = self.login()

    def login(self):
        """Login the website by the credentials, and keep the session..

        :return: False if login fail, or True if success.
        """
        # Touching the login page to get the initialized session.
        self.session.get(Winha.URLS['ELOGON_URL'], headers=Winha.HEAD)

        # Posting the authentication data to the server.
        self.session.post(Winha.URLS['LOGIN_URL'], data=self.auth_data, headers=Winha.HEAD)

        # Touching the emainval page.
        response = self.session.get(Winha.URLS['EMAINVAL_URL'], headers=Winha.HEAD)

        # Determining the login status by the status code of the response.
        if response.status_code == 500:
            return False
        else:
            return True

    def get_student_info_html(self):
        """Gets the HTML document of the student information page.

        :return: student_data_html: the string of the HTML document of the student information page.
        """
        # Requesting the student data.
        response = self.session.get(Winha.URLS['EHENKILO_URL'], headers=Winha.HEAD)

        # Getting the text of the response.
        student_data_html = response.text
        return student_data_html

    def get_student_info(self):
        """Parses the HTML document of the student information page, in order to get the desired data.

        :return: a dict: student_data = {'student_id': student_id, 'sex': sex, 'name': name, 'telephone': telephone,
                        'degree_programme': degree_programme, 'estimated_study_time': estimated_study_time,
                        'entering_group': entering_group, 'group': group, 'email': email,
                        'address': address}.
        """
        student_data_html = self.get_student_info_html()

        # soup is a BeautifulSoup object, which represents the document as a nested data structure.
        # 'html.parser' is used for HTML parsing.
        soup = bs4.BeautifulSoup(student_data_html, 'html.parser')

        # By doubling the .next_sibling to jump over the whitespace
        student_id = soup.tr.next_sibling.next_sibling.next_sibling.next_sibling.td.next_sibling.next_sibling.string

        # Creating a list to store telephones for there are two telephones in html
        telephone = []

        # Creating a list to store groups for there are two groups in html
        group = []

        # Based on the HTML document, getting the desired data
        # Finding all <tr> tags.
        for tr in soup.find_all('tr'):
            # If <tr> has <th> child tag then continue.
            if tr.th is not None:
                # Getting the string of the current item.
                item = tr.th.string
                # Getting the string of the current value of the corresponding item.
                value = tr.td.next_sibling.next_sibling.string
                if item == 'Code':
                    # Student_id always starts with 'e'.
                    student_id = 'e' + value
                elif item == 'Sex':
                    sex = value
                elif item == 'Name':
                    name = value
                elif item == 'Degree Programme':
                    degree_programme = value
                elif item == 'Estimated study time':
                    estimated_study_time = value
                elif item == 'Entering group':
                    entering_group = value
                elif item == 'Group':
                    group.append(value)
                elif item == 'Own e-mail':
                    email = value
                elif item == 'Current address':
                    address = value
                elif item == 'Telephones':
                    if value is not None:
                        telephone.append(value)
        student_data = {'student_id': student_id, 'sex': sex, 'name': name, 'telephone': telephone,
                        'degree_programme': degree_programme, 'estimated_study_time': estimated_study_time,
                        'entering_group': entering_group, 'group': group, 'email': email,
                        'address': address}

        return student_data

    def get_courses_html(self):
        """Gets the HTML document of the courses page.

        :return: courses_html: the string of the HTML document of the courses page.
        """
        # Touching the ehopssis page.
        self.session.get(Winha.URLS['EHOPSSIS_URL'], headers=Winha.HEAD)

        # Requesting all of the courses information.
        response = self.session.get(Winha.URLS['EHOPSSIS_KAIKKI_URL'],
                                    headers=Winha.HEAD)

        # Getting the text of the response.
        courses_html = response.text

        return courses_html

    def get_courses(self):
        """Parses the HTML document of the courses page, in order to get the desired data.

        :return: a dict: {'courses': courses}, courses is a list containing course dicts:
        {'name': name, 'credit': credit, 'status': status, 'grade': grade}
        """
        courses_html = self.get_courses_html()

        # soup is a BeautifulSoup object, which represents the document as a nested data structure.
        # 'html.parser' is used for HTML parsing.
        soup = bs4.BeautifulSoup(courses_html, 'html.parser')

        # Initializing the courses list.
        courses = []

        # Based on the HTML document, getting the desired data.
        for nobr in soup.find_all('nobr'):
            a_tags = nobr.find_all('a')
            if a_tags:
                if nobr.nobr is not None:
                    name = nobr.nobr.string.strip()
                else:
                    name = a_tags[0].string.strip()
                details = a_tags[1].string.strip()

                # Using regex group to match different parts: credit, status, grade.
                m = re.match(r'\(([\d,]+)\s*\S+\s*/\s*(\S+)\s*/\s*(\S+)\s*\)', details)

                # Notice that group(0) matches the whole regex expression.
                # Changing the decimal format for easily computing.
                credit = m.group(1).replace(',', '.')
                status = m.group(2)
                grade = m.group(3)

                # Appending the course into courses list.
                course = {'name': name, 'credit': credit, 'status': status, 'grade': grade}
                courses.append(course)
        return {'courses': courses}

    def get_gpa(self, courses):
        """Calculates GPA and grades distribution based on the provided courses.

        :param courses: a dict: {'courses': courses}, courses is a list containing course dicts:
        {'name': name, 'credit': credit, 'status': status, 'grade': grade}.

        :return: courses_result: a dict: {'gpa': gpa, 'grade_distribution': grade_distribution}.
        """

        # Initializing gpa as float type.
        gpa = 0.0
        credits_sum = 0.0
        courses_result = {'gpa': 0, 'grade_distribution': [0, 0, 0, 0, 0, 0]}

        # Getting courses list
        courses = courses['courses']

        for c in courses:
            grade = c['grade']
            credit = eval(c['credit'])
            # Only number grade is considered.
            if grade.isdigit():
                grade = eval(grade)
                # When calculating gpa, the failed course won't be considered.
                if grade != 0:
                    courses_result['grade_distribution'][grade] += 1
                    credits_sum += credit
                    gpa += credit * grade
                if grade == 0:
                    courses_result['grade_distribution'][0] += 1
        # gpa = (grades * credits) / credits
        gpa /= credits_sum

        # Rounding gpa to 3 digits after the decimal point.
        courses_result['gpa'] = round(gpa, 3)
        return courses_result

    def get_current_courses(self, courses):
        """Gets the current courses that are Enrolled or Enrollemnet Accepted but without grade given.

        :param courses: a dict: {'courses': courses}, courses is a list containing course dicts:
        {'name': name, 'credit': credit, 'status': status, 'grade': grade}.

        :return: a dict: {'current_courses': current_courses}, current_courses is a list containing course dicts:
        {'name': name, 'credit': credit, 'status': status, 'grade': grade}.
        """
        # Getting courses list.
        courses = courses['courses']
        current_courses = []
        for c in courses:
            # I = Enrolled; H = Enrollment accepted.
            if c['status'] == 'I' or c['status'] == 'H':
                current_courses.append(c['name'])
        return {'current_courses': current_courses}

    def get_all_data(self):
        """Summarizes all data crawled from Winha to a dict.

        :return: if Login success, return a dict: {'courses': courses, 'student_id': student_id, 'sex': sex,
                        'name': name, 'telephone': telephone,
                        'degree_programme': degree_programme, 'estimated_study_time': estimated_study_time,
                        'entering_group': entering_group, 'group': group, 'email': email,
                        'address': address, 'gpa': gpa, 'grade_distribution': grade_distribution},
        """

        if self.status is True:
            courses = self.get_courses()
            student_data = self.get_student_info()
            gpa = self.get_gpa(courses)
            current_courses = self.get_current_courses(courses)

            # connecting all of the dicts.
            all_data = dict(courses.items() + student_data.items() + gpa.items() + current_courses.items())

            return all_data

        return {'error': 'wrong student_id or password!'}