# -*- coding: utf-8 -*-
"""
    vamk.app.models
    ~~~~~~~~~~~~~~~
    Implements models.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

from vamk.app import db


class Student(db.Model):
    """Student model for mapping the student table containing fields fb_id, stu_id, stu_password, stu_data, courses_calendar,
    tritonia_pin, tritonia_lastname, and tritonia_id.

    """
    id = db.Column(db.Integer, primary_key=True, index=True)
    fb_id = db.Column(db.String(16), unique=True, nullable=False)
    stu_id = db.Column(db.String(32))
    stu_password = db.Column(db.String(32))
    stu_data = db.Column(db.Text)
    is_auto_vamk = db.Column(db.Boolean)
    courses_calendar = db.Column(db.Text)
    tritonia_pin = db.Column(db.String(32))
    tritonia_lastname = db.Column(db.String(32))
    tritonia_id = db.Column(db.String(32))
    is_auto_tritonia = db.Column(db.Boolean)

    def __init__(self, fb_id, stu_id=None, stu_password=None, stu_data=None, courses_calendar=None, tritonia_pin=None,
                 tritonia_lastname=None, tritonia_id=None):
        self.fb_id = fb_id
        self.stu_id = stu_id
        self.stu_password = stu_password
        self.stu_data = stu_data
        self.courses_calendar = courses_calendar
        self.tritonia_pin = tritonia_pin
        self.tritonia_lastname = tritonia_lastname
        self.tritonia_id = tritonia_id
