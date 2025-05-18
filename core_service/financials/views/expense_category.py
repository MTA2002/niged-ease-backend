from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from financials.models.expense_category import ExpenseCategory
from financials.serializers.expense_category import ExpenseCategorySerializer


class ExpenseCategoryListView(APIView):
    @extend_schema(
        description="Get a list of all expense categories",
        responses={200: ExpenseCategorySerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        expense_categories = ExpenseCategory.objects.filter(store_id=store_id)
        serializer = ExpenseCategorySerializer(expense_categories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new expense category",
        request=ExpenseCategorySerializer,
        responses={
            201: ExpenseCategorySerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        serializer = ExpenseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseCategoryDetailView(APIView):
    def get_category(self, id, store_id):
        try:
            category = ExpenseCategory.objects.get(pk=id, store_id=store_id)
            return category
        except ExpenseCategory.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific expense category by ID",
        responses={
            200: ExpenseCategorySerializer,
            404: OpenApiResponse(description="Expense category not found")
        }
    )
    def get(self, request: Request, id, store_id):
        category = self.get_category(id, store_id)
        serializer = ExpenseCategorySerializer(category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update an expense category",
        request=ExpenseCategorySerializer,
        responses={
            200: ExpenseCategorySerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Expense category not found")
        }
    )
    def put(self, request: Request, id, store_id):
        category = self.get_category(id, store_id)
        serializer = ExpenseCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete an expense category",
        responses={
            204: OpenApiResponse(description="Expense category deleted successfully"),
            404: OpenApiResponse(description="Expense category not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        category = self.get_category(id, store_id)
        category.delete()
        return Response({'message': 'Expense category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)