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
        status_logger.debug(
            "{}, {}".format(now_time, request.data)
        )
        logger.debug("client IP: {}".format(self._get_client_ip(request)))

        try:
            instance_id = request.data["instance_id"]
            self._set_instance_active(instance_id)
        except KeyError as e:
            logger.exception(
                "Missing key in POST request payload. {}".format(e.message)
            )
            return failure_response(status.HTTP_400_BAD_REQUEST, str(e.message))

        return Response("atmo phone_home received")

    def _set_instance_active(self, instance_id):
        """
        Set the status of the instance to active
        """
        instance = find_instance(instance_id)
        try:
            status_update = {'tmp_status': ''}
            update_instance_metadata(instance, status_update)
            logger.debug("Set instance status to active")
        except Exception as exc:
            logger.exception("Error occurred updating instance status")
            return Response(exc.message, status=status.HTTP_409_CONFLICT)

    def _check_instance_status(self, instance_id):
        """
        Check if the instance is waiting for phone_home request
        """
        pass

    def _check_client_ip(self, instance_id, ip_addr):
        """
        Check if the request is sent from the said instance (instance id from payload)
        """
        pass

    def _get_client_ip(self, request):
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
