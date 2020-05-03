FROM alpine-python3

# copy crontabs for root user
COPY crontab-example /etc/crontabs/root
# copy current directory to app
COPY . /app

# start crond with log level 8 in foreground, output to stderr
CMD ["crond", "-f", "-d", "8"]