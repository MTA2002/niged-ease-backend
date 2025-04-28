from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from companies.models import SubscriptionPlan
from companies.serializers.subscription_plan import SubscriptionPlanSerializer


class SubscriptionPlanListView(APIView):
    @extend_schema(
        description="Get a list of all subscription plans",
        responses={200: SubscriptionPlanSerializer(many=True)}
    )
    def get(self, request: Request):
        plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new subscription plan",
        request=SubscriptionPlanSerializer,
        responses={
            201: SubscriptionPlanSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPlanDetailView(APIView):
    def get_plan(self, id):
        try:
            plan = SubscriptionPlan.objects.get(pk=id)
            return plan
        except SubscriptionPlan.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific subscription plan by ID",
        responses={
            200: SubscriptionPlanSerializer,
            404: OpenApiResponse(description="Subscription plan not found")
        }
    )
    def get(self, request: Request, id):
        plan = self.get_plan(id)
        serializer = SubscriptionPlanSerializer(plan)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a subscription plan",
        request=SubscriptionPlanSerializer,
        responses={
            200: SubscriptionPlanSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Subscription plan not found")
        }
    )
    def put(self, request: Request, id):
        plan = self.get_plan(id)
        serializer = SubscriptionPlanSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a subscription plan",
        responses={
            204: OpenApiResponse(description="Subscription plan deleted successfully"),
            404: OpenApiResponse(description="Subscription plan not found")
        }
    )
    def delete(self, request: Request, id):
        plan = self.get_plan(id)
        plan.delete()
        return Response({'message': 'Subscription plan deleted successfully'}, status=status.HTTP_204_NO_CONTENT)