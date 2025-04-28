from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from companies.models.currency import Currency
from companies.serializers.currency import CurrencySerializer


class CurrencyListView(APIView):
    @extend_schema(
        description="Get a list of all currencies",
        responses={200: CurrencySerializer(many=True)}
    )
    def get(self, request: Request):
        currencies = Currency.objects.all()
        serializer = CurrencySerializer(currencies, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new currency",
        request=CurrencySerializer,
        responses={
            201: CurrencySerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request):
        serializer = CurrencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrencyDetailView(APIView):
    def get_currency(self, id):
        try:
            currency = Currency.objects.get(pk=id)
            return currency
        except Currency.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific currency by ID",
        responses={
            200: CurrencySerializer,
            404: OpenApiResponse(description="Currency not found")
        }
    )
    def get(self, request: Request, id):
        currency = self.get_currency(id)
        serializer = CurrencySerializer(currency)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a currency",
        request=CurrencySerializer,
        responses={
            200: CurrencySerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Currency not found")
        }
    )
    def put(self, request: Request, id):
        currency = self.get_currency(id)
        serializer = CurrencySerializer(currency, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a currency",
        responses={
            204: OpenApiResponse(description="Currency deleted successfully"),
            404: OpenApiResponse(description="Currency not found")
        }
    )
    def delete(self, request: Request, id):
        currency = self.get_currency(id)
        currency.delete()
        return Response({'message': 'Currency deleted successfully'}, status=status.HTTP_204_NO_CONTENT)