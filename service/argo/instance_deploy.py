"""
Deploy instance.
"""

import os
import time
from django.conf import settings
from threepio import celery_logger
import atmosphere

from service.argo.wf_call import argo_workflow_exec
from service.argo.common import argo_context_from_config, read_argo_config
from service.argo.exception import WorkflowFailed, WorkflowErrored, ArgoConfigFileError


def argo_deploy_instance(
    provider_uuid,
    instance_uuid,
    server_ip,
    username,
    timezone,
):
    """
    run Argo workflow to deploy an instance

    Args:
        provider_uuid (str): provider uuid
        server_ip (str): ip of the server instance
        username (str): username
        timezone (str): timezone of the provider, e.g. America/Arizona

    Raises:
        exc: exception thrown
    """
    try:
        wf_data = _get_workflow_data(
            provider_uuid, server_ip, username, timezone
        )

        wf, status = argo_workflow_exec(
            "instance_deploy.yml",
            provider_uuid,
            wf_data,
            config_file_path=settings.ARGO_CONFIG_FILE_PATH,
            wait=True
        )

        # dump logs
        _dump_deploy_logs(wf, username, instance_uuid)

        celery_logger.debug("ARGO, workflow complete")
        celery_logger.debug(status)

        if not status.success:
            if status.error:
                raise WorkflowErrored(wf.wf_name)
            raise WorkflowFailed(wf.wf_name)
    except Exception as exc:
        celery_logger.debug(
            "ARGO, argo_deploy_instance(), {}, {}".format(type(exc), exc)
        )
        raise exc


def _get_workflow_data(provider_uuid, server_ip, username, timezone):
    """
    Generate the data structure to be passed to the workflow

    Args:
        server_ip (str): ip of the server instance
        username (str): username of the owner of the instance
        timezone (str): timezone of the provider

    Returns:
        dict: {"arguments": {"parameters": [{"name": "", "value": ""}]}}
    """
    wf_data = {"arguments": {"parameters": []}}
    wf_data["arguments"]["parameters"].append(
        {
            "name": "server-ip",
            "value": server_ip
        }
    )
    wf_data["arguments"]["parameters"].append(
        {
            "name": "user",
            "value": username
        }
    )
    wf_data["arguments"]["parameters"].append({"name": "tz", "value": timezone})

    # read zoneinfo from argo config
    config = read_argo_config(
        settings.ARGO_CONFIG_FILE_PATH, provider_uuid=provider_uuid
    )
    wf_data["arguments"]["parameters"].append(
        {
            "name": "zoneinfo",
            "value": config["zoneinfo"]
        }
    )

    # callback token
    if "callback_token" not in config:
        raise ArgoConfigFileError("callback token missing from Argo config")
    wf_data["arguments"]["parameters"].append(
        {
            "name": "callback_token",
            "value": config["callback_token"]
        }
    )

    return wf_data


def _get_workflow_data_for_temp(provider_uuid, server_ip, username, timezone):
    """
    Generate the data structure to be passed to the workflow.
    used with workflow template

    Args:
        server_ip (str): ip of the server instance
        username (str): username of the owner of the instance
        timezone (str): timezone of the provider

    Returns:
        [str]: a list of parameters to be passed to workflow in the form of "key=value"
    """
    wf_data = []
    wf_data.append("server-ip={}".format(server_ip))
    wf_data.append("user={}".format(username))
    wf_data.append("tz={}".format(timezone))

    # read zoneinfo from argo config
    config = read_argo_config(
        settings.ARGO_CONFIG_FILE_PATH, provider_uuid=provider_uuid
    )
    wf_data.append("zoneinfo={}".format(config["zoneinfo"]))

    return wf_data


def _create_deploy_log_dir(username, instance_uuid, timestamp):
    """
    Create directory to dump deploy workflow log,
    example path: base_dir/username/instance_uuid/timestamp/.
    base directory is created if missing

    Args:
        username (str): username of the owner of the instance
        instance_uuid (str): uuid of the instance
        timestamp (str): timestamp of the deploy

    Returns:
        str: path to the directory to dump logs
    """
    base_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(atmosphere.__file__), "..", "logs",
            "atmosphere_deploy.d"
        )
    )

    # create base dir if missing
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    # create deploy log directory if missing
    directory = os.path.join(base_dir, username, instance_uuid, timestamp)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    return directory


def _dump_deploy_logs(wf, username, instance_uuid):
    """
    Dump workflow logs locally

    Args:
        wf (ArgoWorkflow): workflow to dump logs of
        username (str): username of owner of the instance
        instance_uuid (str): uuid of the instance
    """
    try:
        context = argo_context_from_config(settings.ARGO_CONFIG_FILE_PATH)

        timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        log_dir = _create_deploy_log_dir(username, instance_uuid, timestamp)

        # fetch all info about pods in workflow
        nodes = wf.get_nodes(context)

        for node_name, node in nodes.items():
            playbook_name = None
            # try finding playbook filename from parameters
            if "inputs" in node and "parameters" in node["inputs"]:
                for param in node["inputs"]["parameters"]:
                    if param["name"] == "playbook":
                        playbook_name = os.path.basename(param["value"])
                        break
            if playbook_name:
                log_filename = os.path.join(log_dir, playbook_name + ".log")
            else:
                # uses node name if playbook filename is not found
                log_filename = os.path.join(log_dir, node_name + ".log")
            wf.dump_pod_logs(context, node_name, log_filename)
    except Exception as exc:
        celery_logger.debug(
            "ARGO, failed to dump logs for workflow {}, {}".format(
                wf.wf_name, type(exc)
            )
        )
        celery_logger.debug(exc)
