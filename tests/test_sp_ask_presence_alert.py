#tested 
from sp_ask_service_availability_alert import __version__
from sp_ask_service_availability_alert import Service
from sp_ask_service_availability_alert import check_service_and_insert_to_db
from sp_ask_service_availability_alert import check_if_the_service_open
from sp_ask_service_availability_alert import get_presence
from sp_ask_service_availability_alert import find_opening_hours_for_today

# to be tested
from sp_ask_service_availability_alert import send_sms
from sp_ask_service_availability_alert import send_sms_during_off_hours
from sp_ask_service_availability_alert import verify_Ask_service

from freezegun import freeze_time
import datetime
import unittest
import twilio
from twilio.rest import Client
import pytest

def test_version():
    assert __version__ == '0.1.3'

@freeze_time("2012-01-14 03:21:34")
def test_time():
    assert datetime.datetime.today().time() == datetime.datetime(
                                                year=2012, month=1, day=14,
                                                hour=3, minute=21, second=34).time()
@freeze_time("2020-05-05 13:21:34")
def test_check_if_the_service_open():   
    #import pytest; pytest.set_trace()
    time_now = datetime.datetime.today().hour
    result = check_if_the_service_open(time_now)    
    assert True == result   

def test_check_service_and_insert_to_db():
    Service.create_table()
    Service.delete().execute() 
    check_service_and_insert_to_db()
    query = Service.select()
    assert len(query)==3

def test_Service():
    Service.create_table()
    Service.delete().execute() 
    check_service_and_insert_to_db()
    query = Service.select().first()
    assert query.date.day == datetime.datetime.today().day

def test_get_presence():
    Service.delete().execute() 
    get_presence()
    query = Service.select().count()
    assert query == 3

@freeze_time("2020-05-05 13:21:34")
def test_find_opening_hours_for_today():
    time_now = datetime.datetime.today().weekday()
    result = find_opening_hours_for_today(time_now)    
    assert [10, 19] == result   

def test_normalize_sms_address():
        twilio = _twilio_client()
        assert(twilio._normalize_sms_address(
            sms_phone_number='555-123-4567'
        ),
            '+15551234567')



@pytest.mark.skip(reason="Need a valid target to patch for Client")
def test_send_sms(mocker):
    mocker.patch('twilio.rest.Client')
    client = Client("9999", "909099")

    #mocker.patch('client.messages.create')
    send_sms(3, 3, 3)
    client.messages.create.assert_called_once_with(3,3,3)

@pytest.mark.skip(reason="Need a valid target to patch for Client")
def test_send_sms_during_off_hours(mocker):
    mocker.patch('Client')
    client = Client("9999", "909099")

    mocker.patch('client.messages.create')
    send_sms_during_off_hours(3, 3, 3)
    client.messages.create.assert_called_once_with(3,3,3)


