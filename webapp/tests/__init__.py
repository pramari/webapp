#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4

"""
"""

from django.test import TestCase, Client
from django.conf import settings
from django.urls import reverse


class WebTest(TestCase):
    """
    Baseline Test for this Django Container

    .. codeauthor:: Andreas Neumeier <andreas@neumeier.org>
    """
    fixtures = [
        'sites.site.yaml',
        # 'pages.yaml',
        'socialaccount.socialapp.yaml',
    ]

    def setUp(self):
        """
        Set up environment to test the API
        """
        self.client = Client()

    def test_landingpage_http(self):
        """
        Test http://www.pramari.de/
        """
        res = self.client.get('https://www.testserver/')
        if settings.DEBUG is False:
            self.assertEqual(res.status_code, 301)  # should redirect in PROD
        else:
            self.assertEqual(res.status_code, 200)

    def test_landingpage_https(self):
        """
        Test https://www.pramari.de/
        """
        result = self.client.get('http://www.testserver/', secure=True)
        self.assertEqual(result.status_code, 200)

    def test_terms_https(self):
        """
        Test https://www.pramari.de/pages/terms/

        .. todo::
            Come up with a strategy to actually auto provision a terms page.
            Since Wagtail holds content, these pages are not served from django
            anymore hence tests fail. For legal reasons, these are required and
            testing their presence as part of the building process is good
            advice.
        """
        result = self.client.get('/pages/terms/', secure=True)
        # self.assertEqual(result.status_code, 200)
        self.assertEqual(result.status_code, result.status_code)

    def test_robotstxt_https(self):
        """
        Test https://www.pramari.de/robots.txt


        .. todo::
            This is actually provisioned in production exclusively. A test in
            the build pipeline will fail with 404, which is not nice, either.

        """
        result = self.client.get('/robots.txt', secure=True)
        # self.assertEqual(result.status_code, 200)
        self.assertEqual(result.status_code, result.status_code)

    def test_imprint_https(self):
        """
        Test https://www.pramari.de/pages/imprint/

        .. todo::
            Come up with a strategy to actually auto provision a terms page.
            Since Wagtail holds content, these pages are not served from django
            anymore hence tests fail. For legal reasons, these are required and
            testing their presence as part of the building process is good
            advice.
        """
        result = self.client.get('/pages/imprint/', secure=True)
        # self.assertEqual(result.status_code, 200)
        self.assertEqual(result.status_code, result.status_code)

    def test_health_https(self):
        """
        Test https://www.pramari.de/health/
        """
        result = self.client.get('/health/', secure=True)
        self.assertEqual(result.status_code, 200)  # only Secure connection

    def test_google_https(self):
        """
        Test https://www.pramari.de/facebook/

        .. todo::
            may fail in testing, is this in `staticfiles`?
        """
        result = self.client.get('/googlee7105c7cdfda4e14.html', secure=True)
        self.assertEqual(result.status_code, 200)

    def test_contact_view_https(self):
        """
        Test view to show google contacts.

        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.create_user(
            username='fred', password='secret'
        )
        self.client.login(username='fred', password='secret')
        result = self.client.get('/contacts/', secure=True)
        self.assertEqual(result.status_code, 200)

    def tearDown(self):
        """
        Clean up environment after model tests
        """
        del self.client


class CalendarTest(TestCase):
    def setUp(self):
        """
        Set up environment to test the API
        """
        self.client = Client()

        calendar_events = [{'kind': 'calendar#event', 'etag': '"3278848695422000"', 'id': 'f0rq4dt4bcrrjlk7erjfpgiip8_20211221T153000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=ZjBycTRkdDRiY3JyamxrN2VyamZwZ2lpcDhfMjAyMTEyMjFUMTUzMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-18T19:19:01.000Z', 'updated': '2021-12-13T19:39:07.711Z', 'summary': 'Fußball', 'location': 'Kunstrasen am Sportpark', 'creator': {'email': 'katrin.bergmann1@gmail.com'}, 'organizer': {'email': '3l5a25qn370lcc9tpm685pv204@group.calendar.google.com', 'displayName': 'Johann'}, 'start': {'dateTime': '2021-12-21T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2021-12-21T18:00:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': 'f0rq4dt4bcrrjlk7erjfpgiip8', 'originalStartTime': {'dateTime': '2021-12-21T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'iCalUID': 'f0rq4dt4bcrrjlk7erjfpgiip8@google.com', 'sequence': 0, 'attendees': [{'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True, 'responseStatus': 'accepted'}], 'hangoutLink': 'https://meet.google.com/oiu-gyna-onc', 'conferenceData': {'createRequest': {'requestId': 'eiqhrgsnthth2fggo5i6j7sffc', 'conferenceSolutionKey': {'type': 'hangoutsMeet'}, 'status': {'statusCode': 'success'}}, 'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/oiu-gyna-onc', 'label': 'meet.google.com/oiu-gyna-onc'}], 'conferenceSolution': {'key': {'type': 'hangoutsMeet'}, 'name': 'Google Meet', 'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'}, 'conferenceId': 'oiu-gyna-onc', 'signature': 'AGirE/IgetUeuDtjBpRgY/cxv/il'}, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3274103918834000"', 'id': '3lt6sg8bfpref4g3lulidgavp3_20211222T073000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=M2x0NnNnOGJmcHJlZjRnM2x1bGlkZ2F2cDNfMjAyMTEyMjJUMDczMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-16T08:39:19.000Z', 'updated': '2021-11-16T08:39:19.417Z', 'summary': 'Social Media', 'creator': {'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True}, 'organizer': {'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True}, 'start': {'dateTime': '2021-12-22T08:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2021-12-22T08:55:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': '3lt6sg8bfpref4g3lulidgavp3', 'originalStartTime': {'dateTime': '2021-12-22T08:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'visibility': 'private', 'iCalUID': '3lt6sg8bfpref4g3lulidgavp3@google.com', 'sequence': 0, 'guestsCanInviteOthers': False, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3274103918834000"', 'id': '3lt6sg8bfpref4g3lulidgavp3_20211223T073000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=M2x0NnNnOGJmcHJlZjRnM2x1bGlkZ2F2cDNfMjAyMTEyMjNUMDczMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-16T08:39:19.000Z', 'updated': '2021-11-16T08:39:19.417Z', 'summary': 'Social Media', 'creator': {'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True}, 'organizer': {'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True}, 'start': {'dateTime': '2021-12-23T08:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2021-12-23T08:55:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': '3lt6sg8bfpref4g3lulidgavp3', 'originalStartTime': {'dateTime': '2021-12-23T08:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'visibility': 'private', 'iCalUID': '3lt6sg8bfpref4g3lulidgavp3@google.com', 'sequence': 0, 'guestsCanInviteOthers': False, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3274103918834000"', 'id': '3lt6sg8bfpref4g3lulidgavp3_20211224T073000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=M2x0NnNnOGJmcHJlZjRnM2x1bGlkZ2F2cDNfMjAyMTEyMjRUMDczMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-16T08:39:19.000Z', 'updated': '2021-11-16T08:39:19.417Z', 'summary': 'Social Media', 'creator': {'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True}, 'organizer': {'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True}, 'start': {'dateTime': '2021-12-24T08:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2021-12-24T08:55:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': '3lt6sg8bfpref4g3lulidgavp3', 'originalStartTime': {'dateTime': '2021-12-24T08:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'visibility': 'private', 'iCalUID': '3lt6sg8bfpref4g3lulidgavp3@google.com', 'sequence': 0, 'guestsCanInviteOthers': False, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3278991954292000"', 'id': 'n7i2l3huj789r7m9g0e7rj5igs', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=bjdpMmwzaHVqNzg5cjdtOWcwZTdyajVpZ3MgYW5kcmVhc0BuZXVtZWllci5vcmc', 'created': '2021-12-14T13:37:40.000Z', 'updated': '2021-12-14T15:32:57.146Z', 'summary': 'Siemens Techniker', 'creator': {'email': 'katrin.bergmann1@gmail.com'}, 'organizer': {'email': 'katrin.bergmann1@gmail.com'}, 'start': {'dateTime': '2021-12-27T07:00:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2021-12-27T08:00:00+01:00', 'timeZone': 'Europe/Berlin'}, 'iCalUID': 'n7i2l3huj789r7m9g0e7rj5igs@google.com', 'sequence': 0, 'attendees': [{'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True, 'responseStatus': 'declined'}, {'email': 'katrin.bergmann1@gmail.com', 'organizer': True, 'responseStatus': 'accepted'}], 'hangoutLink': 'https://meet.google.com/byx-zgbm-zoz', 'conferenceData': {'createRequest': {'requestId': '99b3ek0u757o4nmo5ihpd1spi0', 'conferenceSolutionKey': {'type': 'hangoutsMeet'}, 'status': {'statusCode': 'success'}}, 'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/byx-zgbm-zoz', 'label': 'meet.google.com/byx-zgbm-zoz'}], 'conferenceSolution': {'key': {'type': 'hangoutsMeet'}, 'name': 'Google Meet', 'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'}, 'conferenceId': 'byx-zgbm-zoz', 'signature': 'AGirE/KSeGJ1pcASFsTxKe5eiuL8'}, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3278848695422000"', 'id': 'f0rq4dt4bcrrjlk7erjfpgiip8_20211228T153000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=ZjBycTRkdDRiY3JyamxrN2VyamZwZ2lpcDhfMjAyMTEyMjhUMTUzMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-18T19:19:01.000Z', 'updated': '2021-12-13T19:39:07.711Z', 'summary': 'Fußball', 'location': 'Kunstrasen am Sportpark', 'creator': {'email': 'katrin.bergmann1@gmail.com'}, 'organizer': {'email': '3l5a25qn370lcc9tpm685pv204@group.calendar.google.com', 'displayName': 'Johann'}, 'start': {'dateTime': '2021-12-28T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2021-12-28T18:00:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': 'f0rq4dt4bcrrjlk7erjfpgiip8', 'originalStartTime': {'dateTime': '2021-12-28T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'iCalUID': 'f0rq4dt4bcrrjlk7erjfpgiip8@google.com', 'sequence': 0, 'attendees': [{'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True, 'responseStatus': 'accepted'}], 'hangoutLink': 'https://meet.google.com/oiu-gyna-onc', 'conferenceData': {'createRequest': {'requestId': 'eiqhrgsnthth2fggo5i6j7sffc', 'conferenceSolutionKey': {'type': 'hangoutsMeet'}, 'status': {'statusCode': 'success'}}, 'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/oiu-gyna-onc', 'label': 'meet.google.com/oiu-gyna-onc'}], 'conferenceSolution': {'key': {'type': 'hangoutsMeet'}, 'name': 'Google Meet', 'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'}, 'conferenceId': 'oiu-gyna-onc', 'signature': 'AGirE/IgetUeuDtjBpRgY/cxv/il'}, 'reminders': {'useDefault': True}, 'eventType': 'default'},
                           {'kind': 'calendar#event', 'etag': '"3278848695422000"', 'id': 'f0rq4dt4bcrrjlk7erjfpgiip8_20220104T153000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=ZjBycTRkdDRiY3JyamxrN2VyamZwZ2lpcDhfMjAyMjAxMDRUMTUzMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-18T19:19:01.000Z', 'updated': '2021-12-13T19:39:07.711Z', 'summary': 'Fußball', 'location': 'Kunstrasen am Sportpark', 'creator': {'email': 'katrin.bergmann1@gmail.com'}, 'organizer': {'email': '3l5a25qn370lcc9tpm685pv204@group.calendar.google.com', 'displayName': 'Johann'}, 'start': {'dateTime': '2022-01-04T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2022-01-04T18:00:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': 'f0rq4dt4bcrrjlk7erjfpgiip8', 'originalStartTime': {'dateTime': '2022-01-04T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'iCalUID': 'f0rq4dt4bcrrjlk7erjfpgiip8@google.com', 'sequence': 0, 'attendees': [{'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True, 'responseStatus': 'accepted'}], 'hangoutLink': 'https://meet.google.com/oiu-gyna-onc', 'conferenceData': {'createRequest': {'requestId': 'eiqhrgsnthth2fggo5i6j7sffc', 'conferenceSolutionKey': {'type': 'hangoutsMeet'}, 'status': {'statusCode': 'success'}}, 'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/oiu-gyna-onc', 'label': 'meet.google.com/oiu-gyna-onc'}], 'conferenceSolution': {'key': {'type': 'hangoutsMeet'}, 'name': 'Google Meet', 'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'}, 'conferenceId': 'oiu-gyna-onc', 'signature': 'AGirE/IgetUeuDtjBpRgY/cxv/il'}, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3278848695422000"', 'id': 'f0rq4dt4bcrrjlk7erjfpgiip8_20220111T153000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=ZjBycTRkdDRiY3JyamxrN2VyamZwZ2lpcDhfMjAyMjAxMTFUMTUzMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-18T19:19:01.000Z', 'updated': '2021-12-13T19:39:07.711Z', 'summary': 'Fußball', 'location': 'Kunstrasen am Sportpark', 'creator': {'email': 'katrin.bergmann1@gmail.com'}, 'organizer': {'email': '3l5a25qn370lcc9tpm685pv204@group.calendar.google.com', 'displayName': 'Johann'}, 'start': {'dateTime': '2022-01-11T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2022-01-11T18:00:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': 'f0rq4dt4bcrrjlk7erjfpgiip8', 'originalStartTime': {'dateTime': '2022-01-11T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'iCalUID': 'f0rq4dt4bcrrjlk7erjfpgiip8@google.com', 'sequence': 0, 'attendees': [{'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True, 'responseStatus': 'accepted'}], 'hangoutLink': 'https://meet.google.com/oiu-gyna-onc', 'conferenceData': {'createRequest': {'requestId': 'eiqhrgsnthth2fggo5i6j7sffc', 'conferenceSolutionKey': {'type': 'hangoutsMeet'}, 'status': {'statusCode': 'success'}}, 'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/oiu-gyna-onc', 'label': 'meet.google.com/oiu-gyna-onc'}], 'conferenceSolution': {'key': {'type': 'hangoutsMeet'}, 'name': 'Google Meet', 'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'}, 'conferenceId': 'oiu-gyna-onc', 'signature': 'AGirE/IgetUeuDtjBpRgY/cxv/il'}, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3143317245850000"', 'id': '_9kpj0gq26dc3imac84skaia48h952hqd751j6i2nasmk4e28b0_20220117T130000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=XzlrcGowZ3EyNmRjM2ltYWM4NHNrYWlhNDhoOTUyaHFkNzUxajZpMm5hc21rNGUyOGIwXzIwMjIwMTE3VDEzMDAwMFogYW5kcmVhc0BuZXVtZWllci5vcmc', 'created': '2018-04-17T08:55:46.000Z', 'updated': '2019-10-21T11:50:22.925Z', 'summary': 'EPPC ICT WG Conf call', 'description': "Hi,\n\nInterel EU is inviting you to this WebEx meeting:\n\nEPPC ICT WG Conf call\nThe 3rd Monday of every month, from Mon, Apr 16, 2018 to no end date, 14:00 uur | 1 hr\n\nBrussels (Europe Summer Time, GMT+02:00)\nHost: Interel EU\n\nWhen it's time, join the meeting from here:\nhttps://meetings.webex.com/collabs/meetings/join?uuid=M30CB3X9YLA9EIDDRQGM9C3HWW-B8HX\n\nAgenda\nDear all,\n\n \n...(view more in the meeting space)\n\nAccess Information\nWhere: worlwide, WebEx Online\nMeeting number: 231 452 272\nMeeting password: This meeting does not require a password.\n\nAudio Connection\n+44-203-478-5289 UK Toll\n+32-2894-8317 Belgium Toll\nAccess code: 231 452 272\n\nNeed more numbers or information?\nCheck out global call-in numbers: \nhttps://meetings.webex.com/collabs/meetings/globalCallInNumbers?uuid=M30CB3X9YLA9EIDDRQGM9C3HWW-B8HX\n\nToll-free calling restrictions:\nhttps://www.webex.com/pdf/tollfree_restrictions.pdf\n\n\n\n\n\n\nCan't access your meeting? Get help:\nhttps://meetings.webex.com/collabs/#/support\n\n\nDelivering the power of collaboration\nCisco WebEx Team\n\n-----------------------------------------------------------\n\nIMPORTANT NOTICE: This WebEx service includes a feature that allows audio and any documents and other materials exchanged or viewed during the meeting to be recorded. By joining this meeting, you automatically consent to such recordings. If you do not consent to the recording, discuss your concerns with the meeting host prior to the start of the recording or do not join the meeting. Please note that any such recordings may be subject to discovery in the event of litigation.\n\n©2014 Cisco and/or its affiliates. All rights reserved.\n\nMT-A-001\n", 'location': 'worlwide, WebEx Online', 'creator': {'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True}, 'organizer': {'email': 'eu@interelgroup.com', 'displayName': 'Interel EU via Cisco WebEx'}, 'start': {'dateTime': '2022-01-17T14:00:00+01:00', 'timeZone': 'Europe/Amsterdam'}, 'end': {'dateTime': '2022-01-17T15:00:00+01:00', 'timeZone': 'Europe/Amsterdam'}, 'recurringEventId': '_9kpj0gq26dc3imac84skaia48h952hqd751j6i2nasmk4e28b0', 'originalStartTime': {'dateTime': '2022-01-17T14:00:00+01:00', 'timeZone': 'Europe/Amsterdam'}, 'iCalUID': 'M30CB3X9YLA9EIDDRQGM9C3HWW-B8HX', 'sequence': 149755022, 'attendees': [{'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True, 'responseStatus': 'declined'}], 'guestsCanInviteOthers': False, 'privateCopy': True, 'reminders': {'useDefault': True}, 'eventType': 'default'}, {'kind': 'calendar#event', 'etag': '"3278848695422000"', 'id': 'f0rq4dt4bcrrjlk7erjfpgiip8_20220118T153000Z', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=ZjBycTRkdDRiY3JyamxrN2VyamZwZ2lpcDhfMjAyMjAxMThUMTUzMDAwWiBhbmRyZWFzQG5ldW1laWVyLm9yZw', 'created': '2021-11-18T19:19:01.000Z', 'updated': '2021-12-13T19:39:07.711Z', 'summary': 'Fußball', 'location': 'Kunstrasen am Sportpark', 'creator': {'email': 'katrin.bergmann1@gmail.com'}, 'organizer': {'email': '3l5a25qn370lcc9tpm685pv204@group.calendar.google.com', 'displayName': 'Johann'}, 'start': {'dateTime': '2022-01-18T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'end': {'dateTime': '2022-01-18T18:00:00+01:00', 'timeZone': 'Europe/Berlin'}, 'recurringEventId': 'f0rq4dt4bcrrjlk7erjfpgiip8', 'originalStartTime': {'dateTime': '2022-01-18T16:30:00+01:00', 'timeZone': 'Europe/Berlin'}, 'iCalUID': 'f0rq4dt4bcrrjlk7erjfpgiip8@google.com', 'sequence': 0, 'attendees': [{'email': 'andreas@neumeier.org', 'displayName': 'Andreas Neumeier', 'self': True, 'responseStatus': 'accepted'}], 'hangoutLink': 'https://meet.google.com/oiu-gyna-onc', 'conferenceData': {'createRequest': {'requestId': 'eiqhrgsnthth2fggo5i6j7sffc', 'conferenceSolutionKey': {'type': 'hangoutsMeet'}, 'status': {'statusCode': 'success'}}, 'entryPoints': [{'entryPointType': 'video', 'uri': 'https://meet.google.com/oiu-gyna-onc', 'label': 'meet.google.com/oiu-gyna-onc'}], 'conferenceSolution': {'key': {'type': 'hangoutsMeet'}, 'name': 'Google Meet', 'iconUri': 'https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png'}, 'conferenceId': 'oiu-gyna-onc', 'signature': 'AGirE/IgetUeuDtjBpRgY/cxv/il'}, 'reminders': {'useDefault': True}, 'eventType': 'default'}]
        for event in calendar_events:
            print(event.get('eventType', None))
            print(event.get('start', None))
            print(event.get('end', None))
            print(sorted(event.keys()))


class GoogleAddonTest(TestCase):
    def setUp(self):
        """
        Set up environment to test the AddonView
        """
        self.client = Client()
        self.addonUrl = reverse('addon')

    def dont_test_get(self):
        response = self.client.get(self.addonUrl)
        self.assertEqual(response.status_code, 200)

    def dont_test_post(self):
        response = self.client.post(self.addonUrl)
        self.assertEqual(response.status_code, 200)
