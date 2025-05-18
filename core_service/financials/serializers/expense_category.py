from rest_framework import serializers
from financials.models.expense_category import ExpenseCategory


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = [
            'id',
            'store_id',
            'name',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'store_id': {'required': True},
            'name': {'required': True}
        }

    def validate_name(self, value):
        """
        Validate that the category name is unique within the store.
        """
        store_id = self.initial_data.get('store_id') # type: ignore
        if store_id:
            if ExpenseCategory.objects.filter(store_id=store_id, name=value).exists():
                raise serializers.ValidationError(
                    "An expense category with this name already exists for this store."
                )
        return value 