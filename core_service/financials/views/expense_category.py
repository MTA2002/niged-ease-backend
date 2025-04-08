from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from financials.models.expense_category import ExpenseCategory
from financials.serializers.expense_category import ExpenseCategorySerializer


class ExpenseCategoryListView(APIView):
    def get(self, request: Request):
        expense_categories = ExpenseCategory.objects.all()
        serializer = ExpenseCategorySerializer(expense_categories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request: Request):
        serializer = ExpenseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseCategoryDetailView(APIView):
    def get_category(self, id):
        try:
            category = ExpenseCategory.objects.get(pk=id)
            return category
        except ExpenseCategory.DoesNotExist:
            raise Http404
    
    def get(self, request: Request, id):
        category = self.get_category(id)
        serializer = ExpenseCategorySerializer(category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, id):
        category = self.get_category(id)
        serializer = ExpenseCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, id):
        category = self.get_category(id)
        category.delete()
        return Response({'message': 'Expense category deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 