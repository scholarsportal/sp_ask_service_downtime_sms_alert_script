FROM python:3.7.7

# copy current directory to app
# the proper credentials for Twillio in .env needs to be installed
COPY . /app
WORKDIR /app
RUN pip install -r test-requirements.txt

RUN ls
CMD pytest -v /app/
#ENTRYPOINT /entrypoint.sh
