import unittest
import mock
import io

from jenkins_helper.jenkins_functions import *
from mock.mock import patch


BUILD_MESSAGE = """
... [Pipeline] { (validate)
... [Pipeline] sh
... + export 'AWS_ACCESS_KEY_ID='
... + export 'AWS_SECRET_ACCESS_KEY='
... + export 'AWS_REGION=us-east-1'
... + make validate_files
... Error after: `person_id` inteager comment '...
... DDL in line 9 from analysis.sql is invalid.
... make[1]: *** [Makefile:97: validate_file] Error 1
... make: *** [Makefile:100: validate_files] Error 2
... [Pipeline] }
"""

test_json = {"test_key": "test_value", "crumb": "test_crumb"}
test_headers = {"Location": "test_location"}
test_executable = {"url": "test_job_run_url"}


class MockResponse:
    def __init__(self, json_data, status_code, **kwargs):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = test_headers
        if self.json_data:
            self.json_data["executable"] = kwargs.get("executable")
            self.json_data["result"] = kwargs.get("status")

    def json(self):
        return self.json_data

    def get(self):
        return self.executable



def mocked_requests_get(*args, **kwargs):
    if args[0][0:27] == "valid_url_return_executable" and kwargs["auth"] == ("valid_user", "valid_token"):
        return MockResponse(test_json, 200, executable=test_executable, **kwargs)
    elif args[0][0:35] == "valid_url_return_in_progress_status" and kwargs["auth"] == ("valid_user", "valid_token"):
        return MockResponse(test_json, 200, status=IN_PROGRESS_MESSAGE, **kwargs)
    elif args[0][0:31] == "valid_url_return_success_status" and kwargs["auth"] == ("valid_user", "valid_token"):
        return MockResponse(test_json, 200, status=SUCCESS_MESSAGE, **kwargs)
    elif args[0][0:31] == "valid_url_return_failure_status" and kwargs["auth"] == ("valid_user", "valid_token"):
        return MockResponse(test_json, 200, status="FAILURE", **kwargs)
    elif args[0][0:9] == "valid_url" and kwargs["auth"] == ("valid_user", "valid_token"):
        return MockResponse(test_json, 200, **kwargs)
    else:
        return MockResponse(None, 404, **kwargs)


class DDLValidatorTest(unittest.TestCase):

    def test_get_regex_message__with_no_regex_rule(self): 
        filtered_message = get_regex_message(BUILD_MESSAGE)
        self.assertEqual(filtered_message, BUILD_MESSAGE)


    def test_get_regex_message__with_regex_rule(self):
        filtered_message = get_regex_message(BUILD_MESSAGE, "KG1ha2UgdmFsaWRhdGVfZmlsZXMpKC4qPykoXFtQaXBlbGluZVxdKQ==", 2)
        expected_filtered_message = """
... Error after: `person_id` inteager comment '...
... DDL in line 9 from analysis.sql is invalid.
... make[1]: *** [Makefile:97: validate_file] Error 1
... make: *** [Makefile:100: validate_files] Error 2
... """
        self.assertEqual(filtered_message, expected_filtered_message)


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_request_response__with_status_code_2xx_and_parse_json_true(self, mocked_requests_get):
        request_reponse = get_request_response("valid_url", "valid_user", "valid_token", parse_json=True)
        expected_request_reponse = test_json
        self.assertEqual(request_reponse, expected_request_reponse)


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_request_response__with_status_code_2xx_and_parse_json_false(self, mocked_requests_get):
        request_reponse = get_request_response("valid_url", "valid_user", "valid_token", parse_json=False)
        expected_request_reponse = mocked_requests_get("valid_url", auth=("valid_user", "valid_token"))
        self.assertEqual(request_reponse.json_data, expected_request_reponse.json_data)
        self.assertEqual(request_reponse.status_code, expected_request_reponse.status_code)


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_request_response__without_status_code_2xx(self, mocked_requests_get):
        request_reponse = get_request_response("invalid_url", "valid_user", "valid_token")
        self.assertIsNone(request_reponse)


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_crumb(self, mocked_requests_get):
        crumb = get_crumb("valid_url", "valid_user", "valid_token")
        self.assertEqual(crumb, test_json["crumb"])


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_queue_job__with_jenkins_parameters(self, mocked_requests_get):
        queue_item_location = queue_job("crumb", "valid_url", "job_name", '{"param":"value"}', "valid_user", "valid_token")
        self.assertEqual(queue_item_location, test_headers["Location"])


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_queue_job__without_jenkins_parameters(self, mocked_requests_get):
        queue_item_location = queue_job("crumb", "valid_url", "job_name", None, "valid_user", "valid_token")
        self.assertEqual(queue_item_location, test_headers["Location"])


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('time.sleep', return_value=None)
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_get_job_run_url__without_response_answer_with_executable(self, mocked_requests_get, mock_sleep, mock_stdout):
        with self.assertRaises(SystemExit) as context:
            job_run_url = get_job_run_url("valid_url", "valid_user", "valid_token", 30)


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('time.sleep', return_value=None)
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_get_job_run_url__with_response_answer_with_executable(self, mocked_requests_get, mock_sleep, mock_stdout):
        job_run_url = get_job_run_url("valid_url_return_executable", "valid_user", "valid_token", 30)
        self.assertEqual(job_run_url, test_executable["url"])


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('time.sleep', return_value=None)
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_job_progress__with_in_progress_status(self, mocked_requests_get, mock_sleep, mock_stdout):
        with self.assertRaises(SystemExit) as context:
            job_progress("valid_url_return_in_progress_status", "valid_user", "valid_token", 30)


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('time.sleep', return_value=None)
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_job_progress__with_failure_status(self, mocked_requests_get, mock_sleep, mock_stdout):
        with self.assertRaises(SystemExit) as context:
            job_progress("valid_url_return_failure_status", "valid_user", "valid_token", 30)


    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('time.sleep', return_value=None)
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_job_progress__with_success_status(self, mocked_requests_get, mock_sleep, mock_stdout):
        job_progress("valid_url_return_success_status", "valid_user", "valid_token", 30)
 
