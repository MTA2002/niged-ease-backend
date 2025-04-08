from rest_framework import serializers
from financials.models.expense_category import ExpenseCategory


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = [
            'id',
            'company',
            'name',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company': {'required': True},
            'name': {'required': True}
        }

    def validate_name(self, value):
        """
        Validate that the category name is unique within the company.
        """
        company = self.initial_data.get('company') # type: ignore
        if company:
            if ExpenseCategory.objects.filter(company=company, name=value).exists():
                raise serializers.ValidationError(
                    "An expense category with this name already exists for this company."
                )
        return value 