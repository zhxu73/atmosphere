"""
Test Argo
"""
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


class TestArgoWorkflowStatus(unittest.TestCase):
    """
    Test ArgoWorkflowStatus
    """

    @responses.activate
    def test_wf_status_running(self):
        """
        Test Running status
        """
        status = self._wf_status("Running")
        self.assertEqual("Running", status.status)
        self.assertIsNotNone(status)
        self.assertFalse(status.complete)
        self.assertFalse(status.error)
        self.assertFalse(status.success)
        self.assertFalse(status.no_status)

    @responses.activate
    def test_wf_status_success(self):
        """
        Test Succeeded status
        """
        status = self._wf_status("Succeeded")
        self.assertIsNotNone(status)
        self.assertEqual("Succeeded", status.status)
        self.assertTrue(status.complete)
        self.assertFalse(status.error)
        self.assertTrue(status.success)
        self.assertFalse(status.no_status)

    @responses.activate
    def test_wf_status_failed(self):
        """
        Test Failed status
        """
        status = self._wf_status("Failed")
        self.assertIsNotNone(status)
        self.assertEqual("Failed", status.status)
        self.assertTrue(status.complete)
        self.assertTrue(status.error)
        self.assertFalse(status.success)
        self.assertFalse(status.no_status)

    @responses.activate
    def test_wf_status_error(self):
        """
        Test Error status
        """
        status = self._wf_status("Error")
        self.assertIsNotNone(status)
        self.assertEqual("Error", status.status)
        self.assertTrue(status.complete)
        self.assertTrue(status.error)
        self.assertFalse(status.success)
        self.assertFalse(status.no_status)

    @responses.activate
    def test_wf_status_none(self):
        """
        Test when wf status is not available
        """
        responses.add(
            **{
                'method':
                    responses.GET,
                'url':
                    'https://localhost:443/api/v1/workflows/ns/hello-world-12345a',
                'body':
                    '{"status": { "nodes": {"hello-world-a1234": {}} } }',
                'status':
                    200,
                'content_type':
                    'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow(cxt, "hello-world-12345a")
        status = wf.status()
        self.assertIsNotNone(status)
        self.assertIsNone(status.status)
        self.assertIsNone(status.complete)
        self.assertIsNone(status.error)
        self.assertIsNone(status.success)
        self.assertTrue(status.no_status)

    @responses.activate
    def test_wf_status_unrecognizable(self):
        """
        Test when wf status is not unrecognizable
        """
        with self.assertRaises(ValueError):
            self._wf_status("Not Unrecognizable Status")

    @responses.activate
    def test_wf_status_http_error(self):
        """
        Test getting status but has HTTP error
        """
        responses.add(
            **{
                'method':
                    responses.GET,
                'url':
                    'https://localhost:443/api/v1/workflows/ns/hello-world-12345a',
                'body':
                    '',
                'status':
                    400,
                'content_type':
                    'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow(cxt, "hello-world-12345a")
        with self.assertRaises(requests.exceptions.HTTPError):
            wf.status()

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
                'method':
                    responses.GET,
                'url':
                    'https://localhost:443/api/v1/workflows/ns/hello-world-12345a',
                'body':
                    '{"status": {"phase": "%s" } }' % wf_status,
                'status':
                    200,
                'content_type':
                    'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow(cxt, "hello-world-12345a")
        return wf.status()


class TestArgoWorkflow(unittest.TestCase):
    """
    Test ArgoWorkflow
    """

    @responses.activate
    def test_wf_get_nodes(self):
        """
        Test getting workflow nodes
        """
        responses.add(
            **{
                'method':
                    responses.GET,
                'url':
                    'https://localhost:443/api/v1/workflows/ns/hello-world-a1234',
                'body':
                    json.dumps(hello_world_wf_success),
                'status':
                    200,
                'content_type':
                    'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow(cxt, "hello-world-a1234")
        nodes = wf.get_nodes()
        self.assertIn("hello-world-a1234", nodes)
        self.assertEqual(len(nodes), 1)

    @responses.activate
    def test_wf_get_def(self):
        """
        Test fetching wf definition
        """
        responses.add(
            **{
                'method':
                    responses.GET,
                'url':
                    'https://localhost:443/api/v1/workflows/ns/hello-world-a1234',
                'body':
                    json.dumps(hello_world_wf_success),
                'status':
                    200,
                'content_type':
                    'application/json'
            }
        )

        cxt = ArgoContext(
            api_host="localhost",
            api_port=443,
            token="token123",
            namespace="ns",
            ssl_verify=True
        )
        wf = ArgoWorkflow(cxt, "hello-world-a1234")
        wf_def = wf.wf_def()
        self.assertEqual(wf_def, hello_world_wf_success)

    @responses.activate
    def test_wf_creation(self):
        """
        Test wf creation
        """
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
        self.assertEqual(wf.context, cxt)

    @responses.activate
    def test_wf_creation_http_error(self):
        """
        Test wf creation but has http error
        """
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
            ArgoWorkflow.create(cxt, hello_world_wf_def)
