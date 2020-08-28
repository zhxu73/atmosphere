"""
Workflow
"""

import os
import time
from threepio import celery_logger as logger


class ArgoWorkflow:
    """
    A generic interface for using Argo Worflow.
    """

    def __init__(self, wf_name):
        """Creates an ArgoWorkflow object from a workflow definition

        Args:
            wf_def (dict): workflow definition read/parsed from yaml
        """
        self._wf_name = wf_name
        self._last_status = None
        self._wf_def = None

    @staticmethod
    def create(context, wf_def, wf_data={}, lint=False):
        """
        Create a running workflow

        Args:
            context (ArgoContext): context to execute the workflow in
            wf_def (dict): workflow definition
            wf_data (dict, optional): workflow data to be pass along. Defaults to {}.
            lint (bool, optional): Whether to submit workflow definition for
                linting first. Defaults to False.

        Returns:
            ArgoWorkflow: ArgoWorkflow object created based on the returned json
        """
        if wf_data:
            wf_def = _populate_wf_data(wf_def, wf_data)

        json_resp = context.client().run_workflow(wf_def)
        wf_name = json_resp["metadata"]["name"]
        return ArgoWorkflow(wf_name)

    @staticmethod
    def create_n_watch(context, wf_def, wf_data={}):
        """
        Create a running workflow, and watch it until completion

        Args:
            context (ArgoContext): context to execute the workflow in
            wf_def (dict): workflow definition
            wf_data (dict, optional): data to be passed to workflow. Defaults to {}.

        Returns:
            (ArgoWorkflow, ArgoWorkflowStatus): workflow and status of the workflow
        """
        wf = ArgoWorkflow.create(context, wf_def, wf_data=wf_data)

        try:
            wf.watch(context, 10, 18)
            if wf.last_status.complete:
                return (wf, wf.last_status)
            wf.watch(context, 60, 1440)
        except Exception as exc:
            logger.debug(
                "ARGO, ArgoWorkflow.create_n_watch(), while watching {}".format(
                    type(exc)
                )
            )
            logger.debug(
                "ARGO, ArgoWorkflow.create_n_watch(), while watching {}".
                format(exc)
            )
            raise exc
        return (wf, wf.last_status)

    def status(self, context):
        """
        Query status of a workflow

        Args:
            context (ArgoContext): context to perform the query

        Returns:
            ArgoWorkflowStatus: status of workflow
        """
        try:
            # get workflow
            json_obj = context.client().get_workflow(
                self._wf_name, fields="status.phase"
            )

            # unknown state
            if "status" not in json_obj or "phase" not in json_obj["status"]:
                self._last_status = ArgoWorkflowStatus(complete=False)
                return self._last_status

            phase = json_obj["status"]["phase"]

            if phase == "Running":
                self._last_status = ArgoWorkflowStatus(complete=False)
                return self._last_status

            if phase == "Succeeded":
                self._last_status = ArgoWorkflowStatus(
                    complete=True, success=True
                )
                return self._last_status

            if phase == "Failed":
                self._last_status = ArgoWorkflowStatus(
                    complete=True, success=False
                )
                return self._last_status

            if phase == "Error":
                self._last_status = ArgoWorkflowStatus(
                    complete=True, success=False, error=True
                )
                return self._last_status

            return ArgoWorkflowStatus()
        except Exception as exc:
            raise exc

    def watch(self, context, interval, repeat_count):
        """
        Watch the status of workflow, until the workflow is complete.
        This call will block as it is busy waiting.
        After a specified number of queries, the call will abort and return last status.

        Args:
            context (ArgoContext): context to perform the query
            interval (int): interval(sec) in between query for status
            repeat_count (int): number of query for status to perform before abort

        Returns:
            ArgoWorkflowStatus: last status of the workflow
        """
        for _ in range(repeat_count):
            status = self.status(context)
            if status.complete:
                return status
            time.sleep(interval)
        return status

    def get_nodes(self, context):
        """
        Get info (io.argoproj.workflow.v1alpha1.NodeStatus) about the nodes
        (including pods) that this workflow consist of.
        Note: not all node has a corrsponding pod

        Args:
            context (ArgoContext): context used

        Returns:
            dict: a dict whose keys are node names, values are info of the corrsponding node
        """
        json_resp = context.client().get_workflow(
            self._wf_name, fields="status.nodes"
        )
        return json_resp["status"]["nodes"]

    def dump_pod_logs(self, context, pod_name, log_file_path):
        """
        Dump logs of a pod in the workflow into a log file at the given path.
        Technically, it is node_name, calling it the method dump_pod_logs & argument
        pod_name is just to conform to the name in the url in swagger doc.

        Args:
            context (ArgoContext): context used to fetch the logs
            pod_name (str): name of the pod
            log_file_path (str): path to the log file
        """
        # find out what pods the workflow is consisted of
        with open(log_file_path, "a+") as log_file:
            logs_lines = context.client().get_log_for_pod_in_workflow(
                self.wf_name, pod_name, container_name="main"
            )
            log_file.write("\n".join(logs_lines))
        logger.debug(
            ("ARGO, log dump for workflow {}, pod {} at: {}\n"
            ).format(self.wf_name, pod_name, log_file_path)
        )

    def dump_logs(self, context, log_dir):
        """
        Dump logs of the workflow into the log directory provided.
        Separate log file for each pods/steps in the workflow, each with the
        filename of {{pod_name}}.log

        Args:
            context (ArgoContext): context used to fetch the logs
            log_dir (str): directory to dump logs into
        """
        # find out what pods the workflow is consisted of
        json_resp = context.client().get_workflow(self.wf_name)
        pod_names = json_resp["status"]["nodes"].keys()

        # dump logs in separate files for each pods
        for pod_name in pod_names:

            filename = "{}.log".format(pod_name)
            log_file_path = os.path.join(log_dir, filename)

            with open(log_file_path, "a+") as dump_file:
                dump_file.write(
                    "workflow {} has {} pods\n".format(
                        self.wf_name, len(pod_names)
                    )
                )
                logs_lines = context.client().get_log_for_pod_in_workflow(
                    self.wf_name, pod_name, container_name="main"
                )
                dump_file.write("\npod {}:\n".format(pod_name))
                dump_file.writelines(logs_lines)
            logger.debug(
                ("ARGO, log dump for workflow {}, pod {} at: {}\n"
                ).format(self.wf_name, pod_name, log_file_path)
            )

    @property
    def wf_name(self):
        """
        Returns:
            str: name of the workflow
        """
        return self._wf_name

    @property
    def last_status(self):
        """
        Returns:
            ArgoWorkflowStatus: last known status of the workflow
        """
        return self._last_status

    def wf_def(self, context, fetch=True):
        """
        Definition of the workflow, will fetch if absent

        Args:
            context (ArgoContext): Argo context
            fetch (bool, optional): whether to fetch or not if present. Defaults to True.
        """
        if self._wf_def and not fetch:
            return self._wf_def
        self._wf_def = context.client().get_workflow(
            self._wf_name, fields="-status"
        )
        return self._wf_def


class ArgoWorkflowStatus:
    """
    Status of a workflow
    """
    __slots__ = ["_complete", "_success", "_error"]
    all_status_literals = [
        "Pending", "Running", "Succeeded", "Skipped", "Failed", "Error",
        "Omitted"
    ]

    def __init__(self, complete=None, success=None, error=None):
        """
        Args:
            complete (bool, optional): whether the workflow has completed
            success (bool, optional): whether the workflow has succeed
            error (bool, optional): whether the workflow has errored out
        """
        self._complete = complete
        self._success = success
        self._error = error

    @property
    def complete(self):
        """
        Returns:
            bool: whether the workflow has completed
        """
        return self._complete

    @property
    def success(self):
        """
        Returns:
            bool: whether the workflow has succeed
        """
        return self._success

    @property
    def error(self):
        """
        Returns:
            bool: whether the workflow has errored out
        """
        return self._error


def _populate_wf_data(wf_def, wf_data):
    """
    Populate the workflow data in the workflow definition.
    Following data are extracted from wf_data (if any) and then injected into the workflow definition.
    - workflow.spec.parameters (wf_data["spec"]["arguments"]["parameters"])
    - workflow.spec.artifacts (wf_data["spec"]["arguments"]["artifacts"])
    - workflow.annotations (wf_data["metadata"]["annotations"])
    - workflow.labels (wf_data["metadata"]["labels"])

    Args:
        wf_def (dict): workflow definition
        wf_data (dict): workflow data to be populated into workflow definition

    Returns:
        dict: workflow definition with the workflow data populated
    """
    if "metadata" in wf_data:
        _populate_wf_metadata(wf_def, wf_data["metadata"])

    if "spec" not in wf_data:
        return wf_def
    if "arguments" in wf_data["spec"]:
        _populate_wf_arguments(wf_def, wf_data["spec"]["arguments"])

    return wf_def


def _populate_wf_metadata(wf_def, metadata):
    # prepare wf_def
    if "metadata" not in wf_def:
        wf_def["metadata"] = {}
    if not isinstance(wf_def["metadata"], dict):
        wf_def["metadata"] = {}

    # populate annotations & labels
    if "annotations" in metadata:
        wf_def["metadata"]["annotations"] = metadata["annotations"]
    if "labels" in metadata:
        wf_def["metadata"]["labels"] = metadata["labels"]
    return wf_def


def _populate_wf_arguments(wf_def, argument):
    # prepare wf_def
    if "spec" not in wf_def:
        wf_def["spec"] = {}
    if not isinstance(wf_def["spec"], dict):
        wf_def["spec"] = {}
    if "arguments" not in wf_def["spec"]:
        wf_def["spec"]["arguments"] = {}
    if not isinstance(wf_def["spec"]["arguments"], dict):
        wf_def["spec"]["arguments"] = {}

    # populate arguments
    if "parameters" in argument:
        wf_def["spec"]["arguments"]["parameters"] = argument["parameters"]
    if "artifacts" in argument:
        wf_def["spec"]["arguments"]["artifacts"] = argument["artifacts"]
    return wf_def
