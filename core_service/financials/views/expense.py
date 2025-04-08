from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from financials.models.expense import Expense
from financials.serializers.expense import ExpenseSerializer


class ExpenseListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all expenses",
        responses={200: ExpenseSerializer(many=True)}
    )
    def get(self, request: Request):
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new expense",
        request_body=ExpenseSerializer,
        responses={
            201: ExpenseSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailView(APIView):
    def get_expense(self, id):
        try:
            expense = Expense.objects.get(pk=id)
            return expense
        except Expense.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific expense by ID",
        responses={
            200: ExpenseSerializer,
            404: "Expense not found"
        }
    )
    def get(self, request: Request, id):
        expense = self.get_expense(id)
        serializer = ExpenseSerializer(expense)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update an expense",
        request_body=ExpenseSerializer,
        responses={
            200: ExpenseSerializer,
            400: "Invalid data",
            404: "Expense not found"
        }
    )
    def put(self, request: Request, id):
        expense = self.get_expense(id)
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete an expense",
        responses={
            204: "Expense deleted successfully",
            404: "Expense not found"
        }
    )
    def delete(self, request: Request, id):
        expense = self.get_expense(id)
        expense.delete()
        return Response({'message': 'Expense deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 