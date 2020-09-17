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
from service.argo.exception import ArgoConfigFileError


def argo_deploy_instance(
    provider_uuid,
    instance_uuid,
    server_ip,
    username,
    timezone,
    redeploy=False
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
            provider_uuid, instance_uuid, server_ip, username, timezone, redeploy=redeploy
        )

        wf, _ = argo_workflow_exec(
            "instance_deploy.yml",
            provider_uuid,
            wf_data,
            config_file_path=settings.ARGO_CONFIG_FILE_PATH,
            wait=False
        )
        celery_logger.debug("ARGO, workflow {} launched".format(wf.wf_name))

    except Exception as exc:
        celery_logger.debug(
            "ARGO, argo_deploy_instance(), {}, {}".format(type(exc), exc)
        )
        raise exc


def _get_workflow_data(
    provider_uuid, instance_uuid, server_ip, username, timezone, redeploy
):
    """
    Generate the data structure to be passed to the workflow

    Args:
        provider_uuid (str): uuid of the provider
        instance_uuid (str): uuid of the instance
        server_ip (str): ip of the server instance
        username (str): username of the owner of the instance
        timezone (str): timezone of the provider

    Raises:
        ArgoConfigFileError: when fields are missing from argo config

    Returns:
        dict: {"spec": {"arguments": {"parameters": [{"name": "", "value": ""}]}}, "metadata": {"labels": {}, "annotations": {}}}
    """

    wf_data = {"spec": {}, "metadata": {}}
    wf_data["spec"] = {"arguments": {"parameters": []}}
    wf_data["metadata"] = {"labels": {}, "annotations": {}}

    # labels & annotations
    wf_data["metadata"]["labels"]["workflow_type"] = "instance_deploy"
    wf_data["metadata"]["labels"]["provider"] = provider_uuid
    wf_data["metadata"]["annotations"]["instance_uuid"] = instance_uuid

    # parameters
    wf_data["spec"]["arguments"]["parameters"].append(
        {
            "name": "server-ip",
            "value": server_ip
        }
    )
    wf_data["spec"]["arguments"]["parameters"].append(
        {
            "name": "user",
            "value": username
        }
    )
    wf_data["spec"]["arguments"]["parameters"].append(
        {
            "name": "tz",
            "value": timezone
        }
    )
    wf_data["spec"]["arguments"]["parameters"].append(
        {
            "name": "redeploy",
            "value": redeploy
        }
    )

    # read zoneinfo from argo config
    config = read_argo_config(
        settings.ARGO_CONFIG_FILE_PATH, provider_uuid=provider_uuid
    )
    if "zoneinfo" not in config:
        raise ArgoConfigFileError("zoneinfo missing from Argo config")
    wf_data["spec"]["arguments"]["parameters"].append(
        {
            "name": "zoneinfo",
            "value": config["zoneinfo"]
        }
    )

    # callback url
    if "callback_url" not in config:
        raise ArgoConfigFileError("callback url missing from Argo config")
    wf_data["spec"]["arguments"]["parameters"].append(
        {
            "name": "callback_url",
            "value": config["callback_url"]
        }
    )

    # callback token
    if "callback_token" not in config:
        raise ArgoConfigFileError("callback token missing from Argo config")
    wf_data["spec"]["arguments"]["parameters"].append(
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


def dump_deploy_logs(wf, username, instance_uuid):
    """
    Dump workflow logs locally

    Args:
        wf (ArgoWorkflow): workflow to dump logs of
        username (str): username of owner of the instance
        instance_uuid (str): uuid of the instance
    """
    try:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
        log_dir = _create_deploy_log_dir(username, instance_uuid, timestamp)

        # fetch all info about pods in workflow
        nodes = wf.get_nodes()

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
            wf.dump_pod_logs(node_name, log_filename)
    except Exception as exc:
        celery_logger.debug(
            "ARGO, failed to dump logs for workflow {}, {}".format(
                wf.wf_name, type(exc)
            )
        )
        celery_logger.debug(exc)
