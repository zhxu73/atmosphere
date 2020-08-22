import unittest

import requests
import responses
import json
import threepio
threepio.logger = threepio.initialize(logger_name="test_logger")
threepio.celery_logger = threepio.initialize(logger_name="test_celery_logger")

from service.argo.wf import ArgoWorkflow
from service.argo.common import ArgoContext
from service.tests.argo_json import hello_world_wf_def, hello_world_wf_success


class TestArgoWorkflowCreation(unittest.TestCase):

    @responses.activate
    def test_wf_creation(self):
        responses.add(
            **{
                'method': responses.POST,
                'url': 'https://localhost:443/api/v1/workflows/ns',
                'body': '{"metadata": {"name": "hello-world-a1234" } }',
                'status': 200,
                'content_type': 'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow.create(cxt, hello_world_wf_def)
        self.assertEqual(wf.wf_name, "hello-world-a1234")

    @responses.activate
    def test_wf_creation_http_error(self):
        responses.add(
            **{
                'method': responses.POST,
                'url': 'https://localhost:443/api/v1/workflows/ns',
                'body': '',
                'status': 400,
                'content_type': 'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        with self.assertRaises(requests.exceptions.HTTPError):
            wf = ArgoWorkflow.create(cxt, hello_world_wf_def)

class TestArgoWorkflowStatus(unittest.TestCase):

    @responses.activate
    def test_wf_status_running(self):
        status = self._wf_status("Running")
        self.assertIsNotNone(status)
        self.assertFalse(status.complete)
        self.assertFalse(status.error)
        self.assertFalse(status.success)

    @responses.activate
    def test_wf_status_success(self):
        status = self._wf_status("Succeeded")
        self.assertIsNotNone(status)
        self.assertTrue(status.complete)
        self.assertFalse(status.error)
        self.assertTrue(status.success)

    @responses.activate
    def test_wf_status_failed(self):
        status = self._wf_status("Failed")
        self.assertIsNotNone(status)
        self.assertTrue(status.complete)
        self.assertIsNone(status.error)
        self.assertFalse(status.success)

    @responses.activate
    def test_wf_status_error(self):
        status = self._wf_status("Error")
        self.assertIsNotNone(status)
        self.assertTrue(status.complete)
        self.assertTrue(status.error)
        self.assertFalse(status.success)

    @responses.activate
    def test_wf_status_http_error(self):
        responses.add(
            **{
                'method': responses.GET,
                'url': 'https://localhost:443/api/v1/workflows/ns/hello-world-12345a',
                'body': '',
                'status': 400,
                'content_type': 'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow("hello-world-12345a")
        with self.assertRaises(requests.exceptions.HTTPError):
            status = wf.status(cxt)

    def _wf_status(self, wf_status):
        """
        get workflow status from mock endpoint

        Args:
            wf_status (str): status string of the workflow in the mock response

        Returns:
            Union[None, ArgoWorkflowStatus]: workflow status
        """
        responses.add(
            **{
                'method': responses.GET,
                'url': 'https://localhost:443/api/v1/workflows/ns/hello-world-12345a',
                'body': '{"status": {"phase": "%s" } }' % wf_status,
                'status': 200,
                'content_type': 'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow("hello-world-12345a")
        return wf.status(cxt)


class TestArgoWorkflow(unittest.TestCase):
    @responses.activate
    def test_wf_get_nodes(self):
        responses.add(
            **{
                'method': responses.GET,
                'url': 'https://localhost:443/api/v1/workflows/ns/hello-world-a1234',
                'body': json.dumps(hello_world_wf_success),
                'status': 200,
                'content_type': 'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow("hello-world-a1234")
        nodes = wf.get_nodes(cxt)
        self.assertIn("hello-world-a1234", nodes)
        self.assertEqual(len(nodes), 1)

