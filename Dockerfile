# pull official base image
FROM us-central1-docker.pkg.dev/splendid-sector-362217/predixtions/auth-gateway:seed-v1.0

# create the appropriate directories
ENV APP_HOME=/home/app
RUN mkdir -p $APP_HOME

# set work directory
WORKDIR $APP_HOME

USER root

# install psycopg2 dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc && \
    apt-get clean

# install dependencies
COPY requirements.txt $APP_HOME/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

#RUN pip install --upgrade setuptools

# create the app user
#RUN addgroup -S app && adduser -S app -G app
RUN adduser --system --group app

# chown all the files to the app user
#RUN chown -R app:app $APP_HOME

RUN chmod +x start.sh

# change to the app user
USER app

EXPOSE 8000

# Start the application
CMD ["/home/app/start.sh"]