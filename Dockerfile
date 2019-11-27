FROM python:3.7.4-alpine

COPY jenkins_helper /jenkins_helper
COPY jenkins_job.py /jenkins_job.py
COPY requirements.txt /requirements.txt
COPY tests /tests

RUN python -m pip install -r requirements.txt
RUN python -m unittest tests.jenkins_functions_test

ENTRYPOINT [ "python", "/jenkins_job.py" ]