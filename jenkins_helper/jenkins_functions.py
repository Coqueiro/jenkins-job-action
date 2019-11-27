import requests
import time
import sys
import os
import re
import json


IN_PROGRESS_MESSAGE = "IN_PROGRESS"
SUCCESS_MESSAGE = "SUCCESS"
INTERVAL_SECONDS = 5


def get_regex_message(text, console_log_regex=None, console_log_regex_group=None):
    if console_log_regex and console_log_regex_group:
        return re.search(console_log_regex, text, re.DOTALL).group(int(console_log_regex_group))
    else:
        return text


def get_request_response(url, jenkins_user, jenkins_token, parse_json=True, **kwargs):
    request_response_object = requests.get(url, auth=(jenkins_user, jenkins_token), **kwargs)
    status_code = request_response_object.status_code
    if status_code >= 200 and status_code < 300:
        request_response = request_response_object.json() if parse_json else request_response_object
        return request_response
    else:
        return None


def get_crumb(jenkins_url, jenkins_user, jenkins_token):
    crumb_data = get_request_response(f"{jenkins_url}/crumbIssuer/api/json", jenkins_user, jenkins_token, headers={'content-type': 'application/json'})
    return crumb_data['crumb']


def queue_job(crumb, jenkins_url, job_name, jenkins_params, jenkins_user, jenkins_token):
    query_string =  ''
    if jenkins_params:
        params = json.loads(jenkins_params)
        query_string = '?' + '&'.join([str(param)+"="+str(params[param]) for param in params])
    job_queue_url = f"{jenkins_url}/job/{job_name}/buildWithParameters{query_string}"
    queue_response = get_request_response(job_queue_url, jenkins_user, jenkins_token, parse_json=False, params={ 'token': jenkins_token }, headers={'Jenkins-Crumb': crumb})
    queue_item_location = queue_response.headers["Location"]
    return queue_item_location


def get_job_run_url(queue_item_location, jenkins_user, jenkins_token):
    job_run_url = None
    timeout_countdown = 30
    
    while job_run_url == None and timeout_countdown > 0:
        try:
            job_run_response = get_request_response(f"{queue_item_location}api/json", jenkins_user, jenkins_token)
            job_run_response_executable = job_run_response.get("executable")
            if job_run_response_executable:
                job_run_url = job_run_response_executable["url"]
        except Exception as e:
            "Do nothing and try again"
        if job_run_url == None:
            timeout_countdown = timeout_countdown - 1
            time.sleep(INTERVAL_SECONDS)

    if job_run_url:
        return job_run_url
    elif timeout_countdown == 0:
        print("Job trigger timed out.")
        sys.exit(1)
    else:
        print("Job trigger failed.")
        sys.exit(1)

    return job_run_url


def job_progress(job_run_url, jenkins_user, jenkins_token):
    job_follow_url = f"{job_run_url}wfapi/describe"
    job_log_url = f"{job_run_url}logText/progressiveText"

    build_response = None
    build_result = IN_PROGRESS_MESSAGE
    timeout_countdown = 30
    while build_result == IN_PROGRESS_MESSAGE and timeout_countdown > 0:
        try:
            build_response = get_request_response(job_follow_url, jenkins_user, jenkins_token)
            build_result = build_response["status"] if build_response else build_result
        except Exception as e:
            "Do nothing and try again"
        if build_result == IN_PROGRESS_MESSAGE:
            timeout_countdown = timeout_countdown - 1
            time.sleep(INTERVAL_SECONDS)

    if build_result==SUCCESS_MESSAGE:
        print("DDL validation with SUCCESS status!")
    elif timeout_countdown == 0:
        print("Job follow timed out.")
        sys.exit(1)
    else:
        print(f"DDL validation with {build_result} status.")
        try:
            log_response = get_request_response(job_log_url, jenkins_user, jenkins_token, parse_json=False).content.decode('utf8')
            print(get_regex_message(log_response))
        except:
            print("Couldn't retrieve log messages.")
        sys.exit(1)