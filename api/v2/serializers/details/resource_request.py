from rest_framework import exceptions, serializers
from core.models import ResourceRequest, Allocation, Quota, Identity, AtmosphereUser as User, IdentityMembership
from api.v2.serializers.summaries import (
    AllocationSummarySerializer,
    IdentitySummarySerializer,
    UserSummarySerializer,
    ProviderSummarySerializer,
    QuotaSummarySerializer,
)
from api.v2.serializers.fields import (
    IdentityRelatedField, StatusTypeRelatedField
)
from api.v2.serializers.fields.base import UUIDHyperlinkedIdentityField


class UserRelatedField(serializers.PrimaryKeyRelatedField):

    def get_queryset(self):
        return User.objects.all()

    def to_representation(self, value):
        user = User.objects.get(pk=value.pk)
        serializer = UserSummarySerializer(user, context=self.context)
        return serializer.data


class AllocationRelatedField(serializers.RelatedField):

    def get_queryset(self):
        return Allocation.objects.all()

    def to_representation(self, value):
        if value.pk is None:
            return None

        allocation = Allocation.objects.get(pk=value.pk)
        serializer = AllocationSummarySerializer(
            allocation,
            context=self.context)
        return serializer.data

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        if isinstance(data, dict):
            identity = data.get("id", None)
        else:
            identity = data
        try:
            return queryset.get(id=identity)
        except:
            raise exceptions.ValidationError(
                "Allocation with id '%s' does not exist."
                % identity
            )


class QuotaRelatedField(serializers.RelatedField):

    def get_queryset(self):
        return Quota.objects.all()

    def to_representation(self, value):
        if value.pk is None:
            return None

        quota = Quota.objects.get(pk=value.pk)
        serializer = QuotaSummarySerializer(quota, context=self.context)
        return serializer.data

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        if isinstance(data, dict):
            identity = data.get("id", None)
        else:
            identity = data
        try:
            return queryset.get(id=identity)
        except:
            raise exceptions.ValidationError(
                "Quota with id '%s' does not exist."
                % identity
            )


class ResourceRequestSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.CharField(read_only=True)
    url = UUIDHyperlinkedIdentityField(
        view_name='api:v2:resourcerequest-detail',
    )
    created_by = UserRelatedField(read_only=True)
    user = UserSummarySerializer(
        source='membership.identity.created_by',
        read_only=True)
    identity = IdentityRelatedField(source='membership.identity')
    provider = ProviderSummarySerializer(
        source='membership.identity.provider',
        read_only=True)
    status = StatusTypeRelatedField(allow_null=True, required=False)
    quota = QuotaRelatedField(queryset=Quota.objects.all(),
                              allow_null=True,
                              required=False)

    allocation = AllocationRelatedField(queryset=Allocation.objects.all(),
                                        allow_null=True,
                                        required=False)

    # TODO should be refactored to not use SerializerMethodField()
    current_quota = serializers.SerializerMethodField()
    current_allocation = serializers.SerializerMethodField()

    def get_current_quota(self, request):
        user_membership = IdentityMembership.objects.get(
            id=request.membership_id)
        return user_membership.quota.id if user_membership.quota else None

    def get_current_allocation(self, request):
        user_membership = IdentityMembership.objects.get(
            id=request.membership_id)
        return user_membership.allocation.id if user_membership.allocation else None

    class Meta:
        model = ResourceRequest
        fields = (
            'id',
            'uuid',
            'url',
            'request',
            'description',
            'status',
            'created_by',
            'user',
            'identity',
            'provider',
            'admin_message',
            'quota',
            'allocation',
            'current_quota',
            'current_allocation'
        )


class UserResourceRequestSerializer(ResourceRequestSerializer):
    def validate_status(self, value):
        if str(value) not in ["pending", "closed"]:
            raise serializers.ValidationError("Users can only open and close requests.")
        return value
