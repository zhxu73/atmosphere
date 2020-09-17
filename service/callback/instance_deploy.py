"""
Callback handler for instance_deploy workflow
"""
from rtwo.driver import OSDriver
from threepio import logger

from core.models import Instance
from service.cache import get_cached_driver
from service.tasks.driver import get_deploy_chain_second_half, update_metadata
from service.callback.common import WorkflowCallbackHandler
from service.argo.wf import ArgoWorkflow
from service.argo.instance_deploy import dump_deploy_logs
from service.argo.common import argo_context_from_config


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

        if "redeploy" not in json_payload:
            raise KeyError("missing redeploy")
        if isinstance(json_payload["redeploy"], str) or isinstance(
            json_payload["redeploy"], unicode
        ):
            if json_payload["redeploy"] not in["false", "true", "False", "True"]:
                raise ValueError(
                    "redeploy is not a recognizable string, {}".format(
                        json_payload["redeploy"]
                    )
                )
        elif not isinstance(json_payload["redeploy"], bool):
            raise ValueError(
                "redeploy not string or bool, {}".format(
                    type(json_payload["redeploy"])
                )
            )

    def handle(self, workflow_name, json_payload):
        """
        Handle the workflow callback.
        Continue the rest of the deployment if workflow succeeded.
        Declare deploy failure if workflow not succeeded (Error, Failed, etc.).

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

        if not isinstance(json_payload["redeploy"], bool):
            if json_payload["redeploy"] in ["true", "True"]:
                redeploy = True
            elif json_payload["redeploy"] in ["false", "False"]:
                redeploy = False
        else:
            redeploy = json_payload["redeploy"]

        # dump logs
        context = argo_context_from_config()
        wf = ArgoWorkflow(context, workflow_name)
        dump_deploy_logs(wf, username, instance_uuid)

        # handle callback based on wf status
        wf_status = json_payload["workflow_status"]
        if wf_status == "Succeeded":
            continue_deployment(instance_uuid, identity, username, redeploy)
        else:
            deploy_workflow_failed(
                workflow_name, instance_uuid, identity, username
            )


def continue_deployment(instance_uuid, core_identity, username, redeploy):
    """
    Continue the 2nd half of the deployment after the workflow

    Args:
        instance_uuid (str): uuid  of the instance that is deploying by the workflow
        core_identity (core.models.Identity): identity associated with the instance
        username (str): username of the owner

    Raises:
        ValueError: No OS Instance Found
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
        redeploy=redeploy
    )
    chain.apply_async()


def deploy_workflow_failed(
    workflow_name, instance_uuid, core_identity, username
):
    """
    Declare the deployment as failed, change instance status

    Args:
        workflow_name (str): name of the workflow failed
        instance_uuid (str): uuid  of the instance that is deploying by the workflow
        core_identity (core.models.Identity): identity associated with the instance
        username (str): username of the owner

    Raises:
        ValueError: No OS Instance Found
        exc: exception while launching updating metadata task
    """
    # find the OSInstance
    driver = get_cached_driver(identity=core_identity)
    instance = driver.get_instance(instance_uuid)
    if not instance:
        raise ValueError("no OS instance found")

    try:
        metadata = {
            'tmp_status': 'deploy_error',
            'fault_message': "workflow {} failed".format(workflow_name),
            'fault_trace': ""
        }
        update_metadata.s(
            OSDriver,
            driver.provider,
            driver.identity,
            instance.id,
            metadata,
            replace_metadata=False
        ).apply_async()
        # Send deploy email
        logger.debug(
            "deploy_workflow_failed(), user {}, instance {}, workflow {}".
            format(username, instance_uuid, workflow_name)
        )
    except Exception as exc:
        logger.warn(exc)
        raise exc
