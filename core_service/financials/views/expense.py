from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from financials.models.expense import Expense
from financials.serializers.expense import ExpenseSerializer


class ExpenseListView(APIView):
    @extend_schema(
        description="Get a list of all expenses",
        responses={200: ExpenseSerializer(many=True)}
    )
    def get(self, request: Request):
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new expense",
        request=ExpenseSerializer,
        responses={
            201: ExpenseSerializer,
            400: OpenApiResponse(description="Invalid data")
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
    
    @extend_schema(
        description="Get a specific expense by ID",
        responses={
            200: ExpenseSerializer,
            404: OpenApiResponse(description="Expense not found")
        }
    )
    def get(self, request: Request, id):
        expense = self.get_expense(id)
        serializer = ExpenseSerializer(expense)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update an expense",
        request=ExpenseSerializer,
        responses={
            200: ExpenseSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Expense not found")
        }
    )
    def put(self, request: Request, id):
        expense = self.get_expense(id)
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete an expense",
        responses={
            204: OpenApiResponse(description="Expense deleted successfully"),
            404: OpenApiResponse(description="Expense not found")
        }
    )
    def delete(self, request: Request, id):
        expense = self.get_expense(id)
        expense.delete()
        return Response({'message': 'Expense deleted successfully'}, status=status.HTTP_204_NO_CONTENT)