[
![PyPI](https://img.shields.io/pypi/v/ask_schools.svg)
![PyPI](https://img.shields.io/pypi/pyversions/ask_schools.svg)
![PyPI](https://img.shields.io/github/license/guinslym/ask_schools.svg)
](https://pypi.org/project/ask_schools/)
[![TravisCI](https://travis-ci.org/guinslym/ask_schools.svg?branch=master)](https://travis-ci.org/guinslym/ask_schools)

<hr/>

## SP ASK Service SMS Alert script

<p>
Script to ping our 3  main LibraryH3lp services (web, clavardez, sms) and if any of those queues are closed during standard Ask opening Hours for more than 10 minutes then this script will send an SMS to the Scholars-Portal Ask coordinator
<br/>
If the service is close and one of the queue is still open due that an operator had stayed connected then an SMS notification will be sent to the SP Ask coordinator
</p>


## Screenshots
This is a mockup, it will only send if one of the services has been down for at least 10 minutes
<p float="left">
    <img src="screenshots/result_sms.png" width="400"/>
</p>

## Installation


**SP ASK Service SMS Alert** is not a package but a **script** and can run by typing this in the terminal:

```
## using pip 
pip install -r test-requirements.txt
python sp_ask_service_availability_alert.py

## or using poetry
poetry install 
poetry run python sp_ask_service_availability_alert.py

## if Using the Makefile
make setup 
# then.. 
make run
```
In addition it is useful to execute it from **crontab**
`*/10 * * * * python sp_ask_service_availability_alert.py`


## Requirement
1.  This script requires a TWILIO account credentials to send SMS 
2.  This script requires a .env file 

```text

# .env
ACCOUNT_SID="Twillio account sid"
AUTH_TOKEN="twillio auth token"
FROM="phone number"
TO="phone number"
ENVIRONMENT="STAGING or PRODUCTION"
```

## Docker

```text
docker-compose run smsapp-test


----------- coverage: platform linux, python 3.7.7-final-0 -----------
Name                                   Stmts   Miss  Cover
----------------------------------------------------------
log_setup.py                              28      0   100%
sp_ask_service_availability_alert.py     163     66    60%
tests/__init__.py                          0      0   100%
tests/test_sp_ask_presence_alert.py      104      0   100%
----------------------------------------------------------
TOTAL                                    295     66    78%
Coverage HTML written to dir coverage-output/coverage/html
Coverage XML written to file coverage-output/coverage/cov_odesi_coverage.xml


Results (38.78s):
      13 passed
```


## Todo

1.  Replace SMS with email to ASK SP inbox
2.  Add tests
3.  Add Cronjob in Dockerfile
4.  Move the logic to create a [Mobile app](https://github.com/guinslym/sp_ask_dashboard_mobile_app_layout)




