APP=jenkins-job-action
BUMP_LEVEL?=patch
VERSION=`cat VERSION`


python:
	@INPUT_JENKINS_URL=${INPUT_JENKINS_URL} \
	 INPUT_JENKINS_USER=${INPUT_JENKINS_USER} \
	 INPUT_JENKINS_TOKEN=${INPUT_JENKINS_TOKEN} \
	 INPUT_JOB_NAME=${INPUT_JOB_NAME} \
	 INPUT_JENKINS_PARAMS=${INPUT_JENKINS_PARAMS} \
	 INPUT_CONSOLE_LOG_REGEX=${INPUT_CONSOLE_LOG_REGEX} \
	 INPUT_CONSOLE_LOG_REGEX_GROUP=${INPUT_CONSOLE_LOG_REGEX_GROUP} \
	 python3 jenkins_job.py

build:
	@docker build -t "gympass/${APP}" .

run:
	@docker run \
		-e INPUT_JENKINS_URL \
		-e INPUT_JENKINS_USER \
		-e INPUT_JENKINS_TOKEN \
		-e INPUT_JOB_NAME \
		-e INPUT_JENKINS_PARAMS \
	 	-e INPUT_CONSOLE_LOG_REGEX \
	 	-e INPUT_CONSOLE_LOG_REGEX_GROUP \
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