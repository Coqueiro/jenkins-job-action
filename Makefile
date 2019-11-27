APP=jenkins-job-action
BUMP_LEVEL?=patch
VERSION=`cat VERSION`

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
	@python3 -m pip install mock==3.0.5
	@python3 -m unittest tests.jenkins_functions_test

install:
	@python3 -m pip install -r requirements.txt

bump: install test
	@python3 -m pip install bumpversion==0.5.3
	@bumpversion --current-version ${VERSION} ${BUMP_LEVEL} VERSION

git_release:
	@git add VERSION
	@git commit -m "Version bump to ${VERSION}"
	@git push origin master
	@git tag -a -m "Tagging version ${VERSION}" ${VERSION}
	@git push origin ${VERSION}