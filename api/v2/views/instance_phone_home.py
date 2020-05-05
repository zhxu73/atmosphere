import django_filters
from django.db.models import Q
from django.utils.timezone import datetime

from api.v2.serializers.details import InstanceSerializer, InstanceActionSerializer
from api.v2.serializers.post import InstanceSerializer as POST_InstanceSerializer

from core.exceptions import ProviderNotActive
from core.models import GroupMembership, Instance, Identity, UserAllocationSource, Project, AllocationSource
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
        logger.debug(
            "{}, {}".format(now_time, request.data)
        )
        return Response("atmo phone_home received")

