"""
Test instance_deploy workflow
"""
import unittest

from service.argo.instance_deploy import _get_workflow_data


class TestArgoInstanceDeploy(unittest.TestCase):
    def test_get_workflow_data(self):
        self._setup()

        expected_data = {
            "spec":
                {
                    "arguments":
                        {
                            "parameters":
                                [
                                    {
                                        "name": "server-ip",
                                        "value": "127.0.0.1"
                                    }, {
                                        "name": "user",
                                        "value": "test_user123"
                                    }, {
                                        "name": "tz",
                                        "value": "UTC"
                                    },
                                    {
                                        "name":
                                            "zoneinfo",
                                        "value":
                                            "/usr/share/zoneinfo/US/Arizona"
                                    },
                                    {
                                        "name": "callback_url",
                                        "value": "https://localhost/callback"
                                    },
                                    {
                                        "name": "callback_token",
                                        "value": "bbbbbbbbbbbbbbbbbbbbbbbbbb"
                                    }
                                ]
                        }
                },
            "metadata":
                {
                    "labels":
                        {
                            "workflow_type": "instance_deploy",
                            "provider": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                        },
                    "annotations":
                        {
                            "instance_uuid":
                                "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
                        }
                }
        }
        data = _get_workflow_data(
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "127.0.0.1", "test_user123",
            "UTC"
        )
        self.assertEqual(data, expected_data)

    def _setup(self):
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
