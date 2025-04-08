from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from companies.models.currency import Currency
from companies.serializers.currency import CurrencySerializer

class CurrencyListView(APIView):

  @swagger_auto_schema(
    operation_description="Get a list of all currencies",
    responses={200: CurrencySerializer(many=True)}
  )
  def get(self, request: Request):
    currencies = Currency.objects.all()
    serializer = CurrencySerializer(currencies, many = True)

    return Response(data=serializer.data, status=status.HTTP_200_OK)
  
  @swagger_auto_schema(
    operation_description="Create a new currency",
    request_body=CurrencySerializer,
    responses={
      201: CurrencySerializer,
      400: "Invalid data"
    }
  )
  def post(self, request: Request):
    serializer = CurrencySerializer(data = request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrencyDetailView(APIView):

  def get_currency(self, id):
    try:
      currency = Currency.objects.get(pk = id)
      return currency
    except Currency.DoesNotExist:
      raise Http404
  
  @swagger_auto_schema(
    operation_description="Get a specific currency by ID",
    responses={
      200: CurrencySerializer,
      404: "Currency not found"
    }
  )
  def get(self, request: Request, id):
    currency = self.get_currency(id)
    serializer = CurrencySerializer(currency)
    return Response(data=serializer.data, status=status.HTTP_200_OK)

  @swagger_auto_schema(
    operation_description="Update a currency",
    request_body=CurrencySerializer,
    responses={
      200: CurrencySerializer,
      400: "Invalid data",
      404: "Currency not found"
    }
  )
  def put(self, request: Request, id):
    currency = self.get_currency(id)
    serializer = CurrencySerializer(currency, data = request.data)

    if serializer.is_valid():
      serializer.save()
      return Response(data=serializer.data, status=status.HTTP_200_OK)

    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @swagger_auto_schema(
    operation_description="Delete a currency",
    responses={
      204: "Currency deleted successfully",
      404: "Currency not found"
    }
  )
  def delete(self, request: Request, id):
    currency = self.get_currency(id)
    currency.delete()

    return Response({'message': 'Currency deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

