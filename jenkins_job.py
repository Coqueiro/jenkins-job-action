from jenkins_helper.jenkins_functions import *
import sys


jenkins_url = os.environ["INPUT_JENKINS_URL"]
jenkins_user = os.environ["INPUT_JENKINS_USER"]
jenkins_token = os.environ["INPUT_JENKINS_TOKEN"]
job_name = os.environ["INPUT_JOB_NAME"]
jenkins_params = os.environ.get("INPUT_JENKINS_PARAMS")
console_log_regex = os.environ.get("INPUT_CONSOLE_LOG_REGEX")
console_log_regex_group = os.environ.get("INPUT_CONSOLE_LOG_REGEX_GROUP")


def main():
    crumb = get_crumb(jenkins_url, jenkins_user, jenkins_token)
    queue_item_location = queue_job(crumb, jenkins_url, job_name, jenkins_params, jenkins_user, jenkins_token)
    job_run_url = get_job_run_url(queue_item_location, jenkins_user, jenkins_token)
    print(f"Job run URL: {job_run_url.replace('-github', '')}")
    job_progress(job_run_url, jenkins_user, jenkins_token)
    sys.exit(0)

if __name__ == "__main__":
    main()