"""
Test api/v2/workflow_callback endpoint
"""
from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase, APIRequestFactory

from api.v2.views import WorkflowCallbackView


class WorkflowCallbackTests(APITestCase):
    """
    Test api/v2/workflow_callback endpoint
    """
    url_route = 'api:v2:workflow_callback'

    def setUp(self):
        """
        Setup for the test
        """
        self.view = WorkflowCallbackView()
        self.factory = APIRequestFactory()

        # setup a mock argo config
        from django.conf import settings
        import api
        import os
        atmo_root_path = os.path.abspath(
            os.path.join(os.path.dirname(api.__file__), "..")
        )
        settings.ARGO_CONFIG_FILE_PATH = os.path.join(
            atmo_root_path, "travis/argo_config_example.yml"
        )

    def _assert_400_response(self, response, expected_msg=None):
        """
        Assert a 400 BAD_REQUEST response

        Args:
            response (Response): response
            expected_msg (str): expected error message
        """
        self.assertEquals(response.status_code, 400)
        data = response.data
        self.assertIsInstance(data, dict)
        self.assertIn('errors', data)
        self.assertIsInstance(data['errors'], list)
        self.assertEquals(len(data['errors']), 1)
        self.assertIsInstance(data['errors'][0], dict)
        self.assertIn('message', data['errors'][0])
        if expected_msg:
            self.assertEquals(data['errors'][0]['message'], expected_msg)

    def test_wf_callback_missing_wf_name(self):
        """
        Test endpoint with request that is missing workflow name in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'callback_token': "bbbbbbbbbbbbbbbbbbbbbbbbbb",
            'workflow_type': "wf-type-123",
            'workflow_status': "Succeeded"
        },
        response = self.view.post(request)

        self._assert_400_response(response, "missing workflow name")

    def test_wf_callback_wf_name_bad_type(self):
        """
        Test endpoint with request that has bad data type for workflow name
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': 123,
            'callback_token': "bbbbbbbbbbbbbbbbbbbbbbbbbb",
            'workflow_type': "wf-type-123",
            'workflow_status': "Succeeded"
        }
        response = self.view.post(request)
        self._assert_400_response(response, "workflow name ill-formed")

    def test_wf_callback_missing_token(self):
        """
        Test endpoint with request that is missing callback token in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'workflow_type': "instance_deploy",
            'workflow_status': "Succeeded"
        }
        response = self.view.post(request)
        self._assert_400_response(response, "missing callback token")

    def test_wf_callback_token_bad_type(self):
        """
        Test endpoint with request that has bad data type for callback token in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'callback_token': 123,
            'workflow_type': "instance_deploy",
            'workflow_status': "Succeeded"
        }
        response = self.view.post(request)
        self._assert_400_response(response, "callback token ill-formed")

    def test_wf_callback_bad_token(self):
        """
        Test endpoint with request that has bad callback token in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'callback_token': "bad-token-123",
            'workflow_type': "instance_deploy",
            'workflow_status': "Succeeded"
        }
        response = self.view.post(request)
        self._assert_400_response(response, None)
        self.assertTrue(
            "bad callback token" in response.data['errors'][0]['message']
        )

    def test_wf_callback_missing_status(self):
        """
        Test endpoint with request that is missing workflow status in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'callback_token': "bbbbbbbbbbbbbbbbbbbbbbbbbb",
            'workflow_type': "instance_deploy"
        }
        response = self.view.post(request)
        self._assert_400_response(response, "missing workflow status")

    def test_wf_callback_token_bad_status_type(self):
        """
        Test endpoint with request that has bad data type for workflow status in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'callback_token': "bbbbbbbbbbbbbbbbbbbbbbbbbb",
            'workflow_type': "instance_deploy",
            'workflow_status': 123
        }
        response = self.view.post(request)
        self._assert_400_response(response, "workflow status ill-formed")

    def test_wf_callback_token_bad_status_literal(self):
        """
        Test endpoint with request that has unrecognizable workflow status in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'callback_token': "bbbbbbbbbbbbbbbbbbbbbbbbbb",
            'workflow_type': "instance_deploy",
            'workflow_status': "FooBar"
        }
        response = self.view.post(request)
        self._assert_400_response(response, "unrecognized workflow status")
