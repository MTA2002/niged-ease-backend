from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from financials.models.payable import Payable
from financials.serializers.payable import PayableSerializer


class PayableListView(APIView):
    @extend_schema(
        description="Get a list of all payables",
        responses={200: PayableSerializer(many=True)}
    )
    def get(self, request: Request):
        payables = Payable.objects.all()
        serializer = PayableSerializer(payables, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new payable",
        request=PayableSerializer,
        responses={
            201: PayableSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request):
        serializer = PayableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayableDetailView(APIView):
    def get_payable(self, id):
        try:
            payable = Payable.objects.get(pk=id)
            return payable
        except Payable.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific payable by ID",
        responses={
            200: PayableSerializer,
            404: OpenApiResponse(description="Payable not found")
        }
    )
    def get(self, request: Request, id):
        payable = self.get_payable(id)
        serializer = PayableSerializer(payable)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a payable",
        request=PayableSerializer,
        responses={
            200: PayableSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Payable not found")
        }
    )
    def put(self, request: Request, id):
        payable = self.get_payable(id)
        serializer = PayableSerializer(payable, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a payable",
        responses={
            204: OpenApiResponse(description="Payable deleted successfully"),
            404: OpenApiResponse(description="Payable not found")
        }
    )
    def delete(self, request: Request, id):
        payable = self.get_payable(id)
        payable.delete()
        return Response({'message': 'Payable deleted successfully'}, status=status.HTTP_204_NO_CONTENT)