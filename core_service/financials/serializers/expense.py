from rest_framework import serializers
from financials.models.expense import Expense
from financials.serializers.expense_category import ExpenseCategorySerializer


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = [
            'id',
            'company',
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
            'company': {'required': True},
            'amount': {'required': True},
        }

    def validate(self, data):
        """
        Validate that the category belongs to the same company.
        """
        from financials.models.expense_category import ExpenseCategory
        
        category_id = data.get('category_id')
        company = data.get('company')
        
        if category_id and company:
            try:
                category = ExpenseCategory.objects.get(id=category_id, company=company)
                data['category'] = category
            except ExpenseCategory.DoesNotExist:
                raise serializers.ValidationError(
                    "The selected category does not exist or does not belong to this company."
                )
        
        return data 