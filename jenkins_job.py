from jenkins_helper.jenkins_functions import *
import json

jenkins_url = os.environ["jenkins_url"]
jenkins_user = os.environ["jenkins_user"]
jenkins_token = os.environ["jenkins_token"]
job_name = os.environ["job_name"]
jenkins_params = os.environ.get("jenkins_params")
console_log_regex = os.environ.get("console_log_regex")
console_log_regex_group = os.environ.get("console_log_regex_group")


def main():
    crumb = get_crumb(jenkins_url, jenkins_user, jenkins_token)
    queue_item_location = queue_job(crumb, jenkins_url, job_name, jenkins_params, jenkins_user, jenkins_token)
    job_run_url = get_job_run_url(queue_item_location, jenkins_user, jenkins_token)
    print(f"Job run URL: {job_run_url.replace('-github', '')}")
    job_progress(job_run_url, jenkins_user, jenkins_token)


if __name__ == "__main__":
    main()