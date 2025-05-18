from rest_framework import serializers
from financials.models.expense import Expense
from financials.serializers.expense_category import ExpenseCategorySerializer


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = [
            'id',
            'store_id',
            'expense_category',
            'amount',
            'description',
            'currency',
            'payment_mode',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'store_id': {'required': True},
            'amount': {'required': True},
        }

    def validate(self, data):
        """
        Validate that the category belongs to the same store.
        """
        from financials.models.expense_category import ExpenseCategory
        
        category_id = data.get('category_id')
        store_id = data.get('store_id')
        
        if category_id and store_id:
            try:
                category = ExpenseCategory.objects.get(id=category_id, store_id=store_id)
                data['category'] = category
            except ExpenseCategory.DoesNotExist:
                raise serializers.ValidationError(
                    "The selected category does not exist or does not belong to this store."
                )
        
        return data 