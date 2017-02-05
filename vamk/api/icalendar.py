# -*- coding: utf-8 -*-
"""
    vamk.api.calendar
    ~~~~~~~~~~~~~~~~~~
    Implements courses calendar events list generating.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import io
import json

# Relative directory of the courses calendar database based on run.app.
CALENDAR_DB = './data/calendar_db/courses.json'


class Calendar(object):
    """Generates the courses calendar events list based on the given courses.
    """
    def __init__(self, courses):
        """Gets courses from the constructor.

        :param courses: a list containing course dicts {'course_name': course_name, 'group_code': group_code}.
        """
        self.courses = courses

    def get_calendar(self):
        """Gets the courses calendar events list based on the courses.

        :return: student_calendar: calendar events list.
        """
        student_calendar = []

        # Reading from the courses calendar database generated beforehand.
        with io.open(CALENDAR_DB, 'r', encoding='utf-8') as f:
            courses_db = json.loads(f.read())
            for c in self.courses:
                course_name = c['course_name']
                group_code = c['group_code']
                # if the course exists in the courses calendar database.
                if course_name in courses_db:
                    events = courses_db[course_name][group_code]
                else:
                    events = []
                # Do not use append here, because events is a list to be connected with another list.
                student_calendar += events
        return student_calendar

    @staticmethod
    def get_courses_with_group_code(courses):
        """Gets the courses with all of their group codes based on the courses calendar database.

        :param courses: a list: [course_name1, course_name2]
        :return: courses_with_group_code: a list containing dicts {course_name1: [group_code1, group_code2]}.
        """

        courses_with_group_code = []

        # Reading from the courses calendar database generated beforehand.
        with io.open(CALENDAR_DB, 'r', encoding='utf-8') as f:
            courses_db = json.loads(f.read())
            for c in courses:
                # if the course exists in the courses calendar database.
                if c in courses_db:
                    # courses_db[c].keys() is the group_code list.
                    courses_with_group_code.append({c: courses_db[c].keys()})
        return courses_with_group_code
