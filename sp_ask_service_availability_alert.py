__version__ = "0.1.3"

# Python Standard library
from datetime import timedelta
from datetime import datetime
import time
import sys
import atexit

# package installed
from peewee import *
import requests
from twilio.rest import Client
from environs import Env

env = Env()
# Read .env into os.environ
env.read_env()
account_sid = env("ACCOUNT_SID", "fdghdfgh")
auth_token = env("AUTH_TOKEN", "rter")

# loggin system
from log_setup import get_log_formatter

app_log = get_log_formatter()

# Constant
environment = env("ENVIRONMENT", "STAGING")
print(environment)
if environment == "STAGING":
    queues = ["practice-webinars", "scholars-portal"]
else:
    queues = ["scholars-portal", "scholars-portal-txt", "clavardez"]


start_url = "https://ca.libraryh3lp.com/presence/jid/"
end_url = "/chat.ca.libraryh3lp.com/text"


def get_db(db_filename):
    db = SqliteDatabase(
        db_filename, pragmas={"journal_mode": "wal", "cache_size": -1024 * 64}
    )
    return db


if environment == "STAGING":
    app_log.warning("Staging environment")
    print("Staging environment")
    min_alert_minute = 3
    time_to_sleep = 3
    db = get_db("test_sms.db")
else:
    min_alert_minute = 10
    time_to_sleep = 60
    db = get_db("presence.db")

@atexit.register
def delete_table_at_exit():
    try:
        app_log.info("delete table at exit")
        print("delete table at exit")
        Service.delete().execute()
    except:
        app_log.warning("unable to delete table")


class Service(Model):
    """Database Table
        Record queue/service and their Status to
        AVAILABLE,
        UNAVAILABLE,
    """

    queue = CharField(max_length=30, null=False)
    status = CharField(max_length=30, null=False)
    date = DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db

    def __str__(self):
        return "{0}:{1} :\t\t{2}".format("Queue", self.queue, self.status)

    def __repr__(self):
        return "{0}:{1} :\t{2}".format("Queue", self.queue, self.status)


def check_service_and_insert_to_db():
    """Each minutes during Opening Hours
        a script ping the Main
        queues to know their status

        -scholars-portal-txt
        -scholars-portal
        -clavardez
    """
    for queue in queues:
        url = start_url + queue + end_url
        try:
            response = requests.get(url).content
            response = response.decode("utf-8")
            Service.insert(queue=queue, status=response).execute()
        except Exception as e:
            app_log.error("Can't add value in database" + str(e))
            pass


def check_if_the_service_open(my_current_time):
    """Verify if the service is currently open

    Returns:
        [Boolean] -- If the service is open?
    """
    start, end = find_opening_hours_for_today()
    current_hour = my_current_time

    result = (current_hour >= start) and (current_hour <= end)
    return result


def get_presence():
    """Insert the presence status in DB
    Go online and check each Service Presence Status
    and insert it in the DB

    i.e. Does the ASK SMS service is open?
    """
    Service.create_table()
    check_service_and_insert_to_db()
    query = Service.select()
    queues = [service.queue for service in query]
    print(len(queues))
    for service in query:
        print(service)


def send_sms(sms_message_content, schedule):
    """Will send an SMS to Scholars Portal - Ask Coordinator

    SECRETS: Require .env file or Environment variables

    Arguments:
        web {int} -- Number of Downtime in minutes
        clavardez {int} -- Number of Downtime in minutes
        sms {int} -- Number of Downtime in minutes
    """
    try:
        app_log.info("sending sms")
        print("sending sms")
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=sms_message_content, from_=env("FROM"), to=env("TO")
        )
    except:
        app_log.warning("ERROR while sending sms")


def send_sms_during_off_hours():
    """Send SMS is the status is different than
    UNAVAILABLE
    during off hours

    Arguments:
        min_alert_minute {[int]} -- Minimum minute of uptime
    """

    # don't send sms for those status
    off_hours_status = ["dnd", "unavailable", "away"]
    result = Service.select().where((Service.status == "available"))
    print(result)

    # if openned more than 3 minutes
    if len(result) >= 3:
        clavardez = len(
            Service.select().where(
                (Service.status != "unavailable") & (Service.queue == "clavardez")
            )
        )
        sms = len(
            Service.select().where(
                (Service.status != "unavailable")
                & (Service.queue == "scholars-portal-txt")
            )
        )
        web = len(
            Service.select().where(
                (Service.status != "unavailable") & (Service.queue == "scholars-portal")
            )
        )
        practice = len(
            Service.select().where(
                (Service.status != "unavailable") & (Service.queue == "practice-webinars")
            )
        )

        time_now = time.strftime("%X %Z %x")
        try:
            sms_message_content = "Sent: {0}\nOFF HOURS \nAsk Service Uptime\nDuring Off Hours\nweb-en:\t{1} min\nweb-fr:\t{2} min\nSMS:\t{3} min\n".format(
                time_now, web, clavardez, sms
            )
        except:
            app_log.warning("Can't write sms_message_content in off-hours")
        app_log.info("Will send a message off hours ")
        send_sms(sms_message_content, "OFF Hours")
        app_log.info("Have sent an SMS during OFF hours")


def should_send_sms(this_hour):
    """If Ask Service is down for at least 10 minutes (min_alert_minute)
        during Ask opening hours
            then send a SMS

    Arguments:
        min_alert_minute {int} -- Minimum minute of downtime
    """

    is_within_Ask_openning_hours = check_if_the_service_open(this_hour)

    if is_within_Ask_openning_hours == True:
        # retrieve how many time those services were 'unavailable'
        fr_result = Service.select().where(
            (Service.status != "available") & (Service.queue == "clavardez")
        )
        sms_result = Service.select().where(
            (Service.status != "available") & (Service.queue == "scholars-portal-txt")
        )
        # any_service_ is useful for dev testing
        any_service = Service.select().where((Service.status != "available"))

        predicate_fr_result = len(fr_result) >= min_alert_minute
        predicate_any_service = len(any_service) >= min_alert_minute
        predicate_sms_result = len(sms_result) >= min_alert_minute
        list_of_service = [predicate_fr_result, predicate_sms_result]
        list_of_service_staging = [
            predicate_fr_result,
            predicate_any_service,
            predicate_sms_result,
        ]

        if environment == "STAGING":
            result_service = any(x == True for x in list_of_service_staging)
        else:
            result_service = any(x == True for x in list_of_service)

        return result_service
    # else
    if is_within_Ask_openning_hours == False:
        result = Service.select().where((Service.status == "available"))

        if len(result) >= min_alert_minute:
            return True
        else:
            return False


def send_sms_during_opening_hours():
    clavardez = len(
        Service.select().where(
            (Service.status != "available") & (Service.queue == "clavardez")
        )
    )
    sms = len(
        Service.select().where(
            (Service.status != "available") & (Service.queue == "scholars-portal-txt")
        )
    )
    web = len(
        Service.select().where(
            (Service.status != "available") & (Service.queue == "scholars-portal")
        )
    )

    time_now = time.strftime("%X %Z %x")
    try:
        sms_message_content = "Ask Service Downtime\n{0}\nweb-en:\t{1} min\nweb-fr:\t{2} min\nSMS:\t{3} min\n".format(
            time_now, web, clavardez, sms
        )
    except:
        app_log.warning("Can't write sms_message_content in regular service hour")
    app_log.info("Will send a message ")
    send_sms(sms_message_content, "Ask hours")
    app_log.info("Have sent an SMS")


def find_opening_hours_for_today(day=datetime.today().weekday()):
    # Monday to Friday
    if day >= 0 and day < 4:
        return [10, 19]
    # Saturday
    elif day == 5:
        return [10, 17]
    # Sunday
    else:
        # weekend
        return [12, 17]


def service_availability():
    """Main function
    Verify the status of all service
    """
    Service.create_table()
    Service.delete().execute()
    counter = 0
    while counter < min_alert_minute:
        get_presence()
        time.sleep(time_to_sleep)  # sleep one minute
        app_log.info("sleeping for {0} seconds".format(time_to_sleep))
        counter += 1


if __name__ == "__main__":
    app_log.info("Enter sms-app")
    hour = datetime.now().hour
    is_within_Ask_openning_hours = check_if_the_service_open(hour)

    # Run only on Ask open hours
    if is_within_Ask_openning_hours:
        app_log.info("within Ask opening hours")
        print("whitin Ask opening hours")
        service_availability()
        # After 10 min .. check this
        hour = datetime.now().hour
        result = should_send_sms(hour)
        # if OFF hours
        if result:
            send_sms_during_opening_hours

    else:
        print("off hours")
        app_log.info("Ask off-hours")
        service_availability()
        # After 10 min .. check this
        hour = datetime.now().hour
        result = should_send_sms(hour)
        if result:
            send_sms_during_off_hours()
