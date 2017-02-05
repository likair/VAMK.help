# -*- coding: utf-8 -*-
"""
    vamk.tasks.auto_winha
    ~~~~~~~~~~~~~~~~~~~~~
    Implements automatically checking the grades changes.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import json

import mail
from student import Student
from vamk.api.winha import Winha
from vamk.tasks import session
from vamk.utils.encryption import Encryption

if __name__ == '__main__':
    # Checking if the student subscribes the service.
    for student in session.query(Student).filter_by(is_auto_vamk='1'):
        if student.stu_data:
            print student.stu_id + ': '
            # Instantiating a Winha crawler object by credentials.
            c = Winha(student.stu_id, Encryption.decrypt(student.stu_password))
            # If login success.
            if c.status is True:
                # Crawling all of te data of the students from the school server.
                data = c.get_all_data()

                # Checking if the grades change by the grades distribution.
                if data['grade_distribution'] != json.loads(student.stu_data)['grade_distribution']:
                    student.stu_data = json.dumps(data)
                    # Updating the student information in the database.
                    session.commit()
                    print 'updated'
                    content = """Hi! You have new course(s) grade updated. Check here: https://vamk.help
                    """
                    mail.mail(student.stu_id + '@edu.vamk.fi', content)
                else:
                    print 'no update'

            # If login fail.
            else:
                print 'Login fail!'
