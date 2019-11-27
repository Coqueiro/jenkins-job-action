APP = jenkins-job-action


python:
	@jenkins_url=${jenkins_url} \
	 jenkins_user=${jenkins_user} \
	 jenkins_token=${jenkins_token} \
	 job_name=${job_name} \
	 jenkins_params=${jenkins_params} \
	 console_log_regex=${console_log_regex} \
	 console_log_regex_group=${console_log_regex_group} \
	 python3 jenkins_job.py

build:
	@docker build -t "gympass/${APP}" .

run:
	@docker run \
		-e "jenkins_url=${jenkins_url}" \
		-e jenkins_user=${jenkins_user} \
		-e jenkins_token=${jenkins_token} \
		-e job_name=${job_name} \
		-e jenkins_params=${jenkins_params} \
	 	-e console_log_regex=${console_log_regex} \
	 	-e console_log_regex_group=${console_log_regex_group} \
		"gympass/${APP}"

test:
	@python3 -m unittest tests.jenkins_functions_test