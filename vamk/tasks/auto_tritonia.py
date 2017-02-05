# -*- coding: utf-8 -*-
"""
    vamk.tasks.auto_tritonia
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Implements automatically renewing the books in Tritonia.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import mail
from student import Student
from vamk.api.tritonia import Tritonia
from vamk.tasks import session
from vamk.utils.encryption import Encryption

if __name__ == '__main__':
    # Checking if the student subscribes the service.
    for student in session.query(Student).filter_by(is_auto_tritonia='1'):
        print student.tritonia_id + ': '
        # Instantiating a Tritonia crawler object by credentials.
        c = Tritonia(student.tritonia_id, student.tritonia_lastname, Encryption.decrypt(student.tritonia_pin))
        # If login success.
        if c.status is True:
            # Printing the renewed books to the console.
            print 'Renewed: ' + repr(c.renew_books(c.books))

            # Mailing to the student to notify the results.
            content = """Hi! Your books were renewed. Check here: https://vamk.help
            """
            mail.mail(student.stu_id + '@edu.vamk.fi', content)
        # If login fail.
        else:
            print 'Login fail!'
