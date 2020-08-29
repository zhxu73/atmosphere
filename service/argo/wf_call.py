"""
Execute Argo Workflow
"""

from threepio import celery_logger as logger

from service.argo.common import ArgoContext, argo_lookup_yaml_file, read_argo_config
from service.argo.wf import ArgoWorkflow
from service.argo.wf_temp import ArgoWorkflowTemplate


def argo_workflow_exec(
    workflow_filename,
    provider_uuid,
    workflow_data,
    config_file_path=None,
    wait=False
):
    """
    Execute an specified Argo workflow.
    Find file based on provider.
    Pass argument to workflow.

    Args:
        workflow_filename (str): filename of the workflow
        provider_uuid (str): uuid of the provider
        workflow_data (dict): data to be passed to workflow as arguments
        config_file_path (str, optional): path to the config file. will use the
            default one from the setting if None. Defaults to None.
        wait (bool, optional): wait for workflow to complete. Defaults to False.

    Returns:
        (ArgoWorkflow, ArgoWorkflowStatus): workflow and status of the workflow
    """
    try:
        # read configuration from file
        config = read_argo_config(
            config_file_path=config_file_path, provider_uuid=provider_uuid
        )

        # find the workflow definition & construct workflow
        wf_def = argo_lookup_yaml_file(
            config["workflow_base_dir"], workflow_filename, provider_uuid
        )

        # construct workflow context
        context = ArgoContext(config=config)

        # execute
        if wait:
            result = ArgoWorkflow.create_n_watch(context, wf_def, workflow_data)
            return result
        wf = ArgoWorkflow.create(context, wf_def, workflow_data)
        return (wf, None)
    except Exception as exc:
        logger.exception(
            "ARGO, argo_workflow_exec(), {} {}".format(type(exc), exc)
        )
        raise exc


def argo_wf_template_exec(
    wf_template_filename,
    provider_uuid,
    workflow_data,
    config_file_path=None,
    wait=False
):
    """
    Execute an specified Argo workflow.
    Find file based on provider.
    Pass argument to workflow.

    Args:
        wf_template_filename (str): filename of the workflow
        provider_uuid (str): uuid of the provider
        workflow_data (dict): data to be passed to workflow as arguments
        config_file_path (str, optional): path to the config file. will use the
            default one from the setting if None. Defaults to None.
        wait (bool, optional): wait for workflow to complete. Defaults to False.

    Returns:
        (ArgoWorkflow, dict): workflow and status of the workflow,
            e.g. {"complete": bool, "success": bool, "error": bool}
    """
    try:
        # read configuration from file
        config = read_argo_config(config_file_path=config_file_path)

        # construct workflow context
        context = ArgoContext(config=config)

        # find the workflow definition
        wf_temp_def = argo_lookup_yaml_file(
            config["workflow_base_dir"], wf_template_filename, provider_uuid
        )

        # submit workflow template
        wf_temp = ArgoWorkflowTemplate.create(context, wf_temp_def)
        wf_name = wf_temp.execute(context, wf_param=workflow_data)
        wf = ArgoWorkflow(context, wf_name)

        # polling if needed
        if wait:
            status = wf.watch(10, 18)
            if status.complete:
                return (wf_name, status)
            status = wf.watch(60, 1440)
            return (wf, status)
        return (wf, {"complete": None, "success": None, "error": None})

    except Exception as exc:
        logger.exception(
            "ARGO, argo_wf_template_exec(), {} {}".format(type(exc), exc)
        )
        raise exc
