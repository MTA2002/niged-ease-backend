from django.http import Http404
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse
from companies.models import SubscriptionPlan
from companies.serializers import SubscriptionPlanSerializer


class SubscriptionPlanListView(generics.ListCreateAPIView):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description='List of subscription plans retrieved successfully',
                response=SubscriptionPlanSerializer
            )
        },
        description='Get a list of all active subscription plans'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        responses={
            201: OpenApiResponse(
                description='Subscription plan created successfully',
                response=SubscriptionPlanSerializer
            ),
            400: OpenApiResponse(
                description='Invalid request data'
            )
        },
        description='Create a new subscription plan'
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SubscriptionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    # permission_classes = [IsAuthenticated,]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description='Subscription plan details retrieved successfully',
                response=SubscriptionPlanSerializer
            ),
            404: OpenApiResponse(
                description='Subscription plan not found'
            )
        },
        description='Get details of a specific subscription plan'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description='Subscription plan updated successfully',
                response=SubscriptionPlanSerializer
            ),
            400: OpenApiResponse(
                description='Invalid request data'
            ),
            404: OpenApiResponse(
                description='Subscription plan not found'
            )
        },
        description='Update a subscription plan'
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        responses={
            204: OpenApiResponse(
                description='Subscription plan deleted successfully'
            ),
            404: OpenApiResponse(
                description='Subscription plan not found'
            )
        },
        description='Delete a subscription plan'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    # permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = SubscriptionPlan.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset