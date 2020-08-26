"""
Callback handler for instance_deploy workflow
"""
from rtwo.driver import OSDriver
from threepio import logger

from core.models import Instance
from service.cache import get_cached_driver
from service.tasks.driver import get_deploy_chain_second_half
from service.callback.common import WorkflowCallbackHandler


class InstanceDeployCallbackHandler(WorkflowCallbackHandler):
    """
    Handler for instance_deploy workflow
    """

    def verify(self, workflow_name, json_payload):
        """
        Verify that the data is valid for the callback

        Args:
            workflow_name (str): name of the workflow
            json_payload (dict): request data

        Raises:
            KeyError: missing fields in the request data
            ValueError: some fields in the request data are ill-formed
        """
        if "instance_uuid" not in json_payload:
            raise KeyError("missing instance uuid")
        if not isinstance(
            json_payload["instance_uuid"], str
        ) and not isinstance(json_payload["instance_uuid"], unicode):
            raise ValueError("instance uuid not string")

        if "username" not in json_payload:
            raise KeyError("missing username")
        if not isinstance(json_payload["username"], str) and not isinstance(
            json_payload["username"], unicode
        ):
            raise ValueError(
                "username not string, {}".format(
                    type(json_payload["username"])
                )
            )

    def handle(self, workflow_name, json_payload):
        """
        Handle the workflow callback

        Args:
            workflow_name (str): name of the workflow
            json_payload (dict): request json data
        """
        username = json_payload["username"]

        instance_uuid = json_payload["instance_uuid"]
        instance = Instance.objects.get(provider_alias=instance_uuid)
        if not instance:
            raise ValueError("no instance found")
        identity = instance.created_by_identity
        logger.debug(
            "WF callback, {}, {}, {}".format(username, instance_uuid, identity)
        )

        continue_deployment(instance_uuid, identity, username)


def continue_deployment(instance_uuid, core_identity, username):
    """
    Continue the 2nd half of the deployment after the workflow

    Args:
        instance_uuid (str): uuid  of the instance that is deploying by the workflow
        core_identity (core.models.Identity): identity associated with the instance
        username (str): username of the owner
    """
    # find the OSInstance
    driver = get_cached_driver(identity=core_identity)
    instance = driver.get_instance(instance_uuid)
    if not instance:
        raise ValueError("no OS instance found")

    # launch task chain of the 2nd half
    chain = get_deploy_chain_second_half(
        OSDriver,
        driver.provider,
        driver.identity,
        instance,
        core_identity,
        username=None,
        redeploy=False
    )
    chain.apply_async()
