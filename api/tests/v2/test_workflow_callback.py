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

    def test_workflow_callback_missing_wf_name(self):
        """
        Test endpoint with request that is missing workflow name in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'callback_token': "token-123",
            'workflow_type': "wf-type-123"
        },
        response = self.view.post(request)

        self.assertEquals(response.status_code, 400)
        data = response.data
        self.assertIsInstance(data, dict)
        self.assertIn('errors', data)
        self.assertIsInstance(data['errors'], list)
        self.assertEquals(len(data['errors']), 1)
        self.assertIsInstance(data['errors'][0], dict)
        self.assertIn('message', data['errors'][0])
        self.assertEquals(data['errors'][0]['message'], 'missing workflow name')

    def test_workflow_callback_wf_name_bad_type(self):
        """
        Test endpoint with request that has bad data type for workflow name
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': 123,
            'callback_token': "token-123",
            'workflow_type': "wf-type-123"
        }
        response = self.view.post(request)

        self.assertEquals(response.status_code, 400)
        data = response.data
        self.assertIsInstance(data, dict)
        self.assertIn('errors', data)
        self.assertIsInstance(data['errors'], list)
        self.assertEquals(len(data['errors']), 1)
        self.assertIsInstance(data['errors'][0], dict)
        self.assertIn('message', data['errors'][0])
        self.assertEquals(
            data['errors'][0]['message'], 'workflow name ill-formed'
        )

    def test_workflow_callback_missing_token(self):
        """
        Test endpoint with request that is missing callback token in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'workflow_type': "instance_deploy"
        }
        response = self.view.post(request)

        self.assertEquals(response.status_code, 400)
        data = response.data
        self.assertIsInstance(data, dict)
        self.assertIn('errors', data)
        self.assertIsInstance(data['errors'], list)
        self.assertEquals(len(data['errors']), 1)
        self.assertIsInstance(data['errors'][0], dict)
        self.assertIn('message', data['errors'][0])
        self.assertEquals(
            data['errors'][0]['message'], 'missing callback token'
        )

    def test_workflow_callback_token_bad_type(self):
        """
        Test endpoint with request that has bad data type for callback token in data
        """
        request = self.factory.post(
            reverse(self.url_route), content_type='application/json'
        )
        request.data = {
            'workflow_name': "wf-name",
            'callback_token': 123,
            'workflow_type': "instance_deploy"
        }
        response = self.view.post(request)

        self.assertEquals(response.status_code, 400)
        data = response.data
        self.assertIsInstance(data, dict)
        self.assertIn('errors', data)
        self.assertIsInstance(data['errors'], list)
        self.assertEquals(len(data['errors']), 1)
        self.assertIsInstance(data['errors'][0], dict)
        self.assertIn('message', data['errors'][0])
        self.assertEquals(
            data['errors'][0]['message'], 'callback token ill-formed'
        )
