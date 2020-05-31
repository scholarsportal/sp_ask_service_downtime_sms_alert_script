# tested
from sp_ask_service_availability_alert import __version__
from sp_ask_service_availability_alert import Service
from sp_ask_service_availability_alert import check_service_and_insert_to_db
from sp_ask_service_availability_alert import check_if_the_service_open
from sp_ask_service_availability_alert import get_presence
from sp_ask_service_availability_alert import find_opening_hours_for_today
from sp_ask_service_availability_alert import queues
from sp_ask_service_availability_alert import service_availability

# to be tested
from sp_ask_service_availability_alert import send_sms
from sp_ask_service_availability_alert import send_sms_during_off_hours
from sp_ask_service_availability_alert import send_sms_during_opening_hours
from sp_ask_service_availability_alert import should_send_sms

# constant
from sp_ask_service_availability_alert import min_alert_minute
from sp_ask_service_availability_alert import time_to_sleep

from freezegun import freeze_time
import datetime
import unittest
import twilio
from twilio.rest import Client
import pytest


class TestTimeWhithinHour(object):
    def test_service_is_open(self):
        this_date = datetime.datetime(2020, 5, 31, 13, 21, 34)
        is_within_Ask_openning_hours = check_if_the_service_open(this_date.hour)
        assert is_within_Ask_openning_hours == True

    def test_should_send_sms(self):
        this_date = datetime.datetime(2020, 5, 31, 13, 21, 34)
        is_within_Ask_openning_hours = check_if_the_service_open(this_date.hour)
        service_availability()
        # Service.create_table()
        Service.delete().execute()
        Service.insert(queue="scholars-portal", status="unavailable").execute()
        Service.insert(queue="scholars-portal", status="unavailable").execute()
        Service.insert(queue="scholars-portal", status="unavailable").execute()
        result = should_send_sms(this_date.hour)
        assert result == True

    def test_should_not_send_sms(self):
        this_date = datetime.datetime(2020, 5, 31, 13, 21, 34)
        is_within_Ask_openning_hours = check_if_the_service_open(this_date.hour)
        service_availability()
        Service.create_table()
        Service.delete().execute()
        Service.insert(queue="scholars-portal", status="available").execute()
        Service.insert(queue="scholars-portal", status="available").execute()
        Service.insert(queue="scholars-portal", status="available").execute()
        result = should_send_sms(this_date.hour)
        assert result == False


class TestTimeOFFHour(object):
    def test_service_is_close(self):
        this_date = datetime.datetime(2020, 5, 31, 11, 21, 34)
        is_within_Ask_openning_hours = check_if_the_service_open(this_date.hour)
        assert is_within_Ask_openning_hours == False

    def test_should_not_send_sms(self):
        this_date = datetime.datetime(2020, 5, 31, 11, 21, 34)
        is_within_Ask_openning_hours = check_if_the_service_open(this_date.hour)
        service_availability()
        Service.create_table()
        Service.delete().execute()
        Service.insert(queue="scholars-portal", status="unavailable").execute()
        Service.insert(queue="scholars-portal", status="unavailable").execute()
        Service.insert(queue="scholars-portal", status="unavailable").execute()
        result = should_send_sms(this_date.hour)
        assert result == False

    def test_should_send_sms(self):
        this_date = datetime.datetime(2020, 5, 31, 11, 21, 34)
        is_within_Ask_openning_hours = check_if_the_service_open(this_date.hour)
        service_availability()
        Service.create_table()
        Service.delete().execute()
        Service.insert(queue="scholars-portal", status="available").execute()
        Service.insert(queue="scholars-portal", status="available").execute()
        Service.insert(queue="scholars-portal", status="available").execute()
        result = should_send_sms(this_date.hour)
        assert result == True


def test_version():
    assert __version__ == "0.1.3"


@freeze_time("2012-01-14 03:21:34")
def test_time():
    assert (
        datetime.datetime.today().time()
        == datetime.datetime(
            year=2012, month=1, day=14, hour=3, minute=21, second=34
        ).time()
    )


@freeze_time("2020-05-05 13:21:34")
def test_check_if_the_service_open():
    # import pytest; pytest.set_trace()
    time_now = datetime.datetime.today().hour
    result = check_if_the_service_open(time_now)
    assert True == result


def test_check_service_and_insert_to_db():
    Service.create_table()
    Service.delete().execute()
    check_service_and_insert_to_db()
    query = Service.select()
    assert len(query) == len(queues)


def test_Service():
    Service.create_table()
    Service.delete().execute()
    check_service_and_insert_to_db()
    query = Service.select().first()
    assert query.date.day == datetime.datetime.today().day


def test_get_presence():
    Service.delete().execute()
    get_presence()
    query = Service.select()
    names = [serv.queue for serv in query]
    query = query.count()
    assert query == len(queues)


@freeze_time("2020-05-05 13:21:34")
def test_find_opening_hours_for_today():
    time_now = datetime.datetime.today().weekday()
    result = find_opening_hours_for_today(time_now)
    assert [10, 19] == result
