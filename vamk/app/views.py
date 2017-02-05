# -*- coding: utf-8 -*-
"""
    vamk.app.views
    ~~~~~~~~~~~~~~
    Implements url routing in Flask.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import json
from functools import wraps

from authomatic.adapters import WerkzeugAdapter
from flask import jsonify
from flask import render_template, request, make_response, redirect, url_for, session
from vamk.api import winha, tritonia, icalendar
from vamk.app import app, authomatic, db
from vamk.app.models import Student
from vamk.utils.encryption import Encryption


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Checks if fb_id is in session.
        """
        if 'fb_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    return render_template('register.html')


@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login(provider_name):
    # response object for the WerkzeugAdapter.
    response = make_response()

    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)

    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # Updating the user to get more info.
            result.user.update()

            # Reading the facebook id of the user.
            fb_id = result.user.id

            # If there is no this facebook id in the database then add a new user.
            if Student.query.filter_by(fb_id=fb_id).first() is None:
                student = Student(fb_id)
                db.session.add(student)
                db.session.commit()

            # Saving fb_id to the session.
            session['fb_id'] = fb_id

            # Redirecting to the dashboard.
            return redirect(url_for('dashboard'))
    return response


@app.route('/logout')
@login_required
def logout():
    # Remove the fb_id from the session.
    session.pop('fb_id', None)

    # Redirecting to the index page.
    return redirect(url_for('index'))


@app.route('/api/student', methods=['POST'])
@login_required
def get_student_info():
    # Getting credentials from request by json format.
    student_id = request.json.get('student_id')
    password = request.json.get('password')

    # Instantiating a Winha crawler object by credentials.
    c = winha.Winha(student_id, password)

    # Returning json format data.
    return jsonify(c.get_all_data())


@app.route('/api/calendar', methods=['POST'])
@login_required
def get_calendar():
    # Getting json format of courses from request
    courses = request.get_json()

    # Instantiating an ICalendar object by courses list.
    i = icalendar.Calendar(courses['courses'])

    # Getting the courses calendar events list.
    calendar = i.get_calendar()

    # Save courses calendar to the database.
    fb_id = session['fb_id']
    student = Student.query.filter_by(fb_id=fb_id).first()
    student.courses_calendar = json.dumps({'calendar': calendar})
    db.session.commit()

    # Returning json format data.
    return jsonify({'calendar': calendar})


@app.route('/api/tritonia/books', methods=['POST'])
@login_required
def get_books():
    # Getting credentials from request by json format.
    login_id = request.json.get('login_id')
    last_name = request.json.get('last_name')
    pin = request.json.get('pin')

    # Instantiating a Tritonia crawler by credentials.
    c = tritonia.Tritonia(login_id, last_name, pin)

    # Returning json format data.
    return jsonify({'books': c.books})


@app.route('/api/tritonia/renew', methods=['POST'])
@login_required
def renew_books():
    # Getting credentials from request by json format.
    credentials = request.json.get('credentials')
    login_id = credentials['login_id']
    last_name = credentials['last_name']
    pin = credentials['pin']

    # Getting books list from request by json format.
    books = request.json.get('books')

    # Instantiating a login_id crawler object by credentials.
    c = tritonia.Tritonia(login_id, last_name, pin)
    c.renew_books(books, check_due=False)

    # Returning json format data.
    return jsonify({'books': c.books})


@app.route('/api/register', methods=['POST'])
@login_required
def update_student():
    # Because login is required, reading fb_id from the session.
    fb_id = session['fb_id']

    # Getting the student based on the fb_id.
    student = Student.query.filter_by(fb_id=fb_id).first()

    # Handling the winha information.
    student.stu_id = request.form['stu_id']
    # Encrypting the password.
    student.stu_password = Encryption.encrypt(request.form['stu_password'])
    if 'checkbox-vamk' in request.form:
        student.is_auto_vamk = True
    else:
        student.is_auto_vamk = False

    # Handling the Tritonia information.
    student.tritonia_id = request.form['tritonia_id']
    student.tritonia_lastname = request.form['tritonia_lastname']
    student.tritonia_pin = Encryption.encrypt(request.form['tritonia_pin'])  # encrypting the pin
    if 'checkbox-tritonia' in request.form:
        student.is_auto_tritonia = True
    else:
        student.is_auto_tritonia = False

    # Committing the data into the database.
    db.session.commit()

    # Redirecting to the dashboard page.
    return redirect(url_for('dashboard'))


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    # Because login is required, reading fb_id from the session.
    fb_id = session['fb_id']

    # Getting the student based on the fb_id.
    student = Student.query.filter_by(fb_id=fb_id).first()

    books = None
    credentials = None

    # if stu_id or stu_password is None, Redirecting to the register page.
    if not student.stu_id or not student.stu_password:
        return render_template("register.html")

    else:
        # Instantiating a Winha crawler object.
        c = winha.Winha(student.stu_id, Encryption.decrypt(student.stu_password))

        # Winha Login fail, redirecting to the register page.
        if c.status is False:
            return render_template("register.html")

        # Winha login success.
        else:
            # Crawling all of te data of the students from the school server.
            data = c.get_all_data()
            # Converting dict to string so as to store in the database.
            student.stu_data = json.dumps(data)
            # Committing the changes to the database.
            db.session.commit()

            # Getting the current courses with group codes based on the data crawled just now.
            current_courses = icalendar.Calendar.get_courses_with_group_code(data['current_courses'])

            # If the Tritonia credential is valid.
            if student.tritonia_id and student.tritonia_lastname and student.tritonia_pin:
                # Building the credentials dict.
                credentials = {'login_id': student.tritonia_id,
                               'last_name': student.tritonia_lastname,
                               'pin': Encryption.decrypt(student.tritonia_pin)}

                # Instantiating a Tritonia crawler object.
                c = tritonia.Tritonia(student.tritonia_id, student.tritonia_lastname,
                                      Encryption.decrypt(student.tritonia_pin))
                # books would be None if login fail.
                books = c.books

            # For Testing
            # data = json.loads(open('./data/student_info_json.json').read())
            # current_courses = calendar.Calendar.get_courses_with_group_code(data['current_courses'])

            return render_template("dashboard.html",
                                   data=data,
                                   current_courses=current_courses,
                                   books=books,
                                   credentials=credentials,
                                   courses_calendar=student.courses_calendar)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html")


@app.errorhandler(405)
def method_not_found(e):
    return render_template("errors/405.html")
