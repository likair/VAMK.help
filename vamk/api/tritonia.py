# -*- coding: utf-8 -*-
"""
    vamk.api.tritonia
    ~~~~~~~~~~~~~~~~~
    Implements tritonia crawler.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import datetime

import bs4
import re
from crawler import Crawler


class Tritonia(Crawler):
    """Inherits Crawler class. Simulates the browser to login in to the Tritonia system, in order to get the desired
    data based on the HTML documents. The desired data in this case are information of books borrowed from Tritonia
    library. And also includes the method for renewing books.
    """

    # Collecting all of the URLs needed.
    URLS = {
        'LOGON_URL': 'https://tria.linneanet.fi/vwebv/login',
        'LOGON_POST_URL': 'https://tria.linneanet.fi/vwebv/login.do',
        'MY_ACCOUNT_URL': 'https://tria.linneanet.fi/vwebv/myAccount',
        'RENEWAL_URL': 'https://tria.linneanet.fi/vwebv/myAccountUpd'
    }

    def __init__(self, login_id=None, last_name=None, pin=None):
        """Constructor for getting login credentials.
        """

        # Initializing the base class Crawler.
        Crawler.__init__(self)

        # Structuring the authentication data into a dict for posting to the server.
        self.auth_data = {'loginType': 'B', 'loginId': login_id, 'lastName': last_name, 'pin': pin,
                          'page.logIn.library': '1@VYKDB20011102005217'}

        self.books = None
        self.content = ''

        # Login the website then other requests can be made with this session and getting the status of login.
        self.status = self.login()
        if self.status is True:
            self.books = self.get_books()

    def login(self):
        """Login the website by the credentials, and keep the session..

        :return: False if login fail, or True if success.
        """
        # Touching the login page to get the initialized session.
        self.session.get(Tritonia.URLS['LOGON_URL'], headers=Tritonia.HEAD)

        # Posting the authentication data to the server
        self.session.post(Tritonia.URLS['LOGON_POST_URL'], data=self.auth_data, headers=Tritonia.HEAD)

        # Getting the response from my account page
        response = self.session.get(Tritonia.URLS['MY_ACCOUNT_URL'], headers=Tritonia.HEAD)
        self.content = response.text

        # Determining the login status by a special string in the HTML document of my account page.
        if '<title>Kirjaudu sis&auml;&auml;n</title>' in self.content:
            return False
        else:
            return True

    def get_books(self):
        """Parses the HTML document of my account page, in order to get the desired data.

        :return: a list containing book dicts {'value': value, 'name': name, 'due': due, 'renewals': renewals}.
        """

        # soup is a BeautifulSoup object, which represents the document as a nested data structure.
        # 'html.parser' is used for HTML parsing.
        soup = bs4.BeautifulSoup(self.content, 'html.parser')

        # Initializing the borrowed books list.
        books = []

        # Based on the HTML document, getting the desired data.
        for tr in soup.findAll('tr', {'class': re.compile(r'resultListRow.*')}):
            value = tr.input['value']
            name = tr.find('td', headers='cellChargedItem').string.strip()
            due = tr.find('td', headers='cellChargedDueDate').string.strip()
            renewals = tr.find('td', headers='cellChargedRenewals').string.strip()

            # Appending the book to books list.
            books.append({'value': value, 'name': name, 'due': due, 'renewals': renewals})

        return books

    def is_book_due(self, book):
        """Determines if a book is due soon by comparing the due date with current date.

        :param book: a dict: {'value': value, 'name': name, 'due': due, 'renewals': renewals}.

        :return: if the book is due soon then return True, or return False
        """

        # Converting the due date from a string to datetime object by the Format '%d.%m.%Y %H:%M:%S',
        # for example: 25.05.2016 19:00:00.
        due_date = datetime.datetime.strptime(book['due'], '%d.%m.%Y %H:%M:%S')

        # Getting the current datetime object.
        now_date = datetime.datetime.now()

        # Two datetime objects subtracting gets a timedelta object to get the available days before due.
        if (due_date - now_date).days < 2:
            return True
        else:
            return False

    def renew_books(self, books, check_due=True):
        """Renews the provided books. If the check_due is True, the due date would be checked before the renewals, or
        just renewing without condition.

        :param books: a list containing book dicts {'value': value, 'name': name, 'due': due, 'renewals': renewals}.
        :param check_due: boolean, determines if check the due date before the renewal.
        :return: a list containing renewed book dicts {'value': value, 'name': name, 'due': due, 'renewals': renewals}.
        """

        due_books = []

        # Building the post data.
        renewal_data = [('renew', 'Request Renewal')]
        for book in books:
            if check_due:
                if self.is_book_due(book):
                    due_books.append(book)
                    renewal_data.append(('selectCharged', book['value']))
            else:
                due_books.append(book)
                renewal_data.append(('selectCharged', book['value']))

        # Posting the renewals data to the server.
        self.session.post(Tritonia.URLS['RENEWAL_URL'], renewal_data, headers=Tritonia.HEAD)

        # Updating the latest books.
        self.content = self.session.get(Tritonia.URLS['MY_ACCOUNT_URL'], headers=Tritonia.HEAD).text
        self.books = self.get_books()

        return due_books
