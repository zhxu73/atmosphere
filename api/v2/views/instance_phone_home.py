import django_filters
from django.db.models import Q
from django.utils.timezone import datetime

from api.v2.serializers.details import InstanceSerializer, InstanceActionSerializer
from api.v2.serializers.post import InstanceSerializer as POST_InstanceSerializer

from core.exceptions import ProviderNotActive
from core.models import GroupMembership, Instance, Identity, UserAllocationSource, Project, AllocationSource
from core.models.instance import find_instance
from core.models.boot_script import _save_scripts_to_instance
from core.models.instance import find_instance
from core.models.instance_action import InstanceAction
from core.query import only_current_instances

from rest_framework import status
from django_filters import rest_framework as filters
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import APIView

from service.tasks.driver import destroy_instance
from service.instance import (
    launch_instance, run_instance_action, update_instance_metadata
)
#from service.tasks.driver import update_metadata
from threepio import logger, status_logger
# Things that go bump
from api.v2.exceptions import (
    failure_response, invalid_creds, connection_failure
)
from api.exceptions import (
    over_quota, under_threshold, size_not_available, over_capacity,
    mount_failed, inactive_provider
)
from service.exceptions import (
    ActionNotAllowed, AllocationBlacklistedError, OverAllocationError,
    OverQuotaError, SizeNotAvailable, HypervisorCapacityError,
    SecurityGroupNotCreated, UnderThresholdError, VolumeAttachConflict,
    VolumeMountConflict, InstanceDoesNotExist
)

class InstancePhoneHomeView(APIView):
    """
    Mock endpoint for phone_home request from cloud-init.
    """
    def post(self, request, format=None):
        """
        Instance notify Atmosphere that the cloud-init script has finished executing
        """

        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(
            "{}, phone_home request received".format(now_time)
        )

        # find instance
        if "instance_id" not in request.data:
            logger.exception("missing instance_id in phone_home request payload, return 400.")
            return failure_response(status.HTTP_400_BAD_REQUEST, "")
        instance_id = request.data["instance_id"]

        instance = find_instance(instance_id)
        if not instance:
            logger.exception("phone_home request, {}, instance not found, return 400.".format(instance_id))
            return failure_response(status.HTTP_400_BAD_REQUEST, "")

        # check if the client/sender of the request has the same IP as
        # the instance itself
        if not _check_client_ip(request, instance):
            logger.debug("phone_home request, {}, sender ip not consistent with the instance ip, return 409".format(instance_id))
            return failure_response(status.HTTP_409_CONFLICT, "")

        # check if the instance is in deploying
        if not _check_instance_status(instance):
            logger.debug("phone_home request, {}, instance is not in 'deploying' state, return 409".format(instance_id))
            return failure_response(status.HTTP_409_CONFLICT, "")

        # set instance status to active
        self._set_instance_active(instance)

        return Response("atmo phone_home received")

def _set_instance_active(instance):
    """
    Set the status of the instance to active
    """
    try:
        status_update = {'tmp_status': ''}
        update_instance_metadata(instance, status_update)
        logger.debug("phone_home request, {}, Set instance status to active".format(instance.provider_alias))
        status_logger.debug("phone_home request, {}, Set instance status to active".format(instance.provider_alias))
    except Exception as exc:
        logger.exception("Error occurred updating instance status")
        return Response(exc.message, status=status.HTTP_409_CONFLICT)

def _check_instance_status(instance):
    """
    Check if the instance is waiting for phone_home request
    """
    last_history = instance.get_last_history()
    logger.debug("phone_home request, {}, instance state: {}".format(instance.id, last_history))
    return last_history.status.name == "deploying" and len(last_history.activity) == 0

def _check_client_ip(request, instance):
    """
    Check if the request is sent from the said instance.
    Return True if same IP
    """
    client_ip = _get_client_ip(request)
    logger.debug("phone_home request, client IP: {}".format(client_ip))
    return client_ip == str(instance.ip_address)

def _get_client_ip(request):
    """
    Fetch the ip of client
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
