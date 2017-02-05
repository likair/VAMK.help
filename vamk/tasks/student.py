# -*- coding: utf-8 -*-
"""
    vamk.tasks.student
    ~~~~~~~~~~~~~~~~~~
    Implements the student model.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

#  Base is a base class from which all mapped classes should inherit.
Base = declarative_base()


class Student(Base):
    """Student model for mapping the student table containing fields fb_id, stu_id, stu_password, stu_data,
    courses_calendar, tritonia_pin, tritonia_lastname, and tritonia_id.
    """
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, index=True)
    fb_id = Column(String(32), unique=True, nullable=False)
    stu_id = Column(String(32))
    stu_password = Column(String(64))
    stu_data = Column(Text)
    is_auto_vamk = Column(Boolean)
    courses_calendar = Column(Text)
    tritonia_pin = Column(String(32))
    tritonia_lastname = Column(String(32))
    tritonia_id = Column(String(32))
    is_auto_tritonia = Column(Boolean)
