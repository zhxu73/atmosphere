"""
Generic workflow callback mechanism
"""
from abc import ABCMeta


class WorkflowCallbackHandler:
    """
    Interface to workflow callback handler
    """
    __metaclass__ = ABCMeta

    def verify(self, workflow_name, json_payload):
        """
        Verify if the json data in the request is valid

        Args:
            workflow_name (str): name of the workflow
            json_payload (dict): json data in the callback request

        Raises:
            NotImplementedError: abstract class
        """
        raise NotImplementedError

    def handle(self, workflow_name, json_payload):
        """
        Handle the callback

        Args:
            workflow_name (str): name of the workflow
            json_payload (dict): json data in the request

        Raises:
            NotImplementedError: abstract class
        """
        raise NotImplementedError
