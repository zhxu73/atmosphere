"""
Argo Workflow callback endpoint
"""

from django.utils.timezone import datetime
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from api.v2.exceptions import failure_response
from threepio import logger
from service.callback import all_handlers
from service.argo.common import read_argo_config


class WorkflowCallbackView(APIView):
    """
    Argo Workflow Callback View
    """

    def post(self, request, format=None):
        """
        Workflow notify Atmosphere that it has finished execution via a POST request

        Args:
            request (rest_framework.request.Request): callback request
            format ([type], optional): [description]. Defaults to None.

        Returns:
            Response: response to the callback request
        """
        try:
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.debug("{}, callback request received".format(now_time))

            failure_resp = _verify_data(request.data)
            if failure_resp:
                return failure_resp

            wf_name = request.data["workflow_name"]
            # check token
            _verify_callback_token(wf_name, request.data["callback_token"])

            # check workflow
            _verify_workflow(wf_name)

            # dispatch to handler
            _dispatch_wf_callback(wf_name, request.data)

            return Response(
                data={"message": "workflow callback received"}, status=200
            )
        except ValueError as exc:
            return failure_response(status.HTTP_400_BAD_REQUEST, str(exc))
        except Exception as exc:
            logger.exception(exc)
            return failure_response(
                status.HTTP_409_CONFLICT,
                "{}, {}".format(str(type(exc)), str(exc))
            )


def _verify_data(req_data):
    # find workflow
    if "workflow_name" not in req_data:
        return failure_response(
            status.HTTP_400_BAD_REQUEST, "missing workflow name"
        )
    if not isinstance(req_data["workflow_name"], str
                     ) and not isinstance(req_data["workflow_name"], unicode):
        return failure_response(
            status.HTTP_400_BAD_REQUEST, "workflow name ill-formed"
        )

    # verify callback token
    if "callback_token" not in req_data:
        return failure_response(
            status.HTTP_400_BAD_REQUEST, "missing callback token"
        )
    if not isinstance(req_data["callback_token"], str
                     ) and not isinstance(req_data["callback_token"], unicode):
        return failure_response(
            status.HTTP_400_BAD_REQUEST, "callback token ill-formed"
        )
    _verify_callback_token(
        req_data["workflow_name"], req_data["callback_token"]
    )
    return None


def _verify_workflow(workflow_name):
    """
    Verify that the workflow does exist, and is allowed to perform callback.
    If verification fails, relevant exceptions will be thrown.

    Args:
        context (ArgoContext): context of the workflow
        workflow_name (str): name of the workflow

    Raises:
        Exception: TODO use specific execption type
    """
    # raise Exception("invalid workflow")
    pass


def _verify_callback_token(workflow_name, callback_token):
    """
    Verify callback token.
    if verification fails, relevant exceptions will be thrown.

    Args:
        workflow_name (str): name of the workflow
        callback_token (str): callback token
    """
    config = read_argo_config()
    if "callback_token" not in config:
        raise Exception("callback token not found in config")
    if config["callback_token"] != callback_token:
        raise ValueError("bad callback token")


def _get_client_ip(request):
    """
    Fetch the ip of client

    Args:
        request (Request): http request from client

    Returns:
        str: ip address of the client
    """
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except KeyError:
        return None


def _dispatch_wf_callback(workflow_name, json_payload):
    """
    Dispatch workflow callback to its appropriate handler

    Args:
        workflow_name (str): name of the workflow
        json_payload (dict): json body of the callback request
    """
    handler_type = all_handlers[json_payload["workflow_type"]]
    if not handler_type:
        raise Exception("unknown workflow type")
    handler = handler_type()
    handler.verify(workflow_name, json_payload)

    handler.handle(workflow_name, json_payload)
