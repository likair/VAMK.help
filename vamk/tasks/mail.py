# -*- coding: utf-8 -*-
"""
    vamk.tasks.mail
    ~~~~~~~~~~~~~~~
    Implements the mailing by mailgun.

    :copyright: (c) 2016 by Likai Ren.
    :license: BSD, see LICENSE for more details.
"""

import requests


def mail(email, text):
    """Mails by mailgun.

    :param email: the email address of the recipient.
    :param text: the content of the mail
    """
    key = 'key-ab152ed054c1ae79c7bd3d3d4e9f8bfd'
    sandbox = 'vamk.help'
    recipient = email
    request_url = 'https://api.mailgun.net/v2/' + sandbox + '/messages'

    request = requests.post(request_url, auth=('api', key), data={
        'from': 'noreply@vamk.help',
        'to': recipient,
        'subject': 'News from VAMK.help',
        'text': text
    })
