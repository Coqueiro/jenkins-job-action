FROM python:3.7.4-alpine

ENV WORK_DIR="/usr/src/app/"

RUN mkdir -p $WORK_DIR

COPY jenkins_helper $WORK_DIR/jenkins_helper
COPY jenkins_job.py $WORK_DIR
COPY requirements.txt $WORK_DIR
COPY tests $WORK_DIR/tests

WORKDIR $WORK_DIR

RUN python -m pip install -r requirements.txt
RUN python -m unittest tests.jenkins_functions_test

ENTRYPOINT [ "python", "jenkins_job.py" ]