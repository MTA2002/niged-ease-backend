from rest_framework import serializers
from financials.models.payment_in import PaymentIn
from transactions.serializers.payment_mode import PaymentModeSerializer
from transactions.models.payment_mode import PaymentMode
from transactions.models import Sale
from django.db import models
from transactions.models.sale_item import SaleItem


class PaymentInSerializer(serializers.ModelSerializer):
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PaymentIn
        fields = [
            'id',
            'store_id',
            'receivable',
            'sale',
            'amount',
            'currency',
            'payment_mode',
            'payment_mode_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'store_id': {'required': True},
            'receivable': {'required': True},
            'sale': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the receivable and sale belong to the same store
        and the payment amount is valid.
        """
        receivable = data.get('receivable')
        sale = data.get('sale')
        store_id = data.get('store_id')
        amount = data.get('amount')
        
        if receivable and store_id and receivable.store_id != store_id:
            raise serializers.ValidationError(
                "The selected receivable does not belong to this store."
            )
            
        if sale and store_id and sale.store_id != store_id:
            raise serializers.ValidationError(
                "The selected sale does not belong to this store."
            )

        if amount <= 0:
            raise serializers.ValidationError(
                "Payment amount must be greater than zero."
            )

        if amount > receivable.amount:
            raise serializers.ValidationError(
                "Payment amount cannot exceed the receivable amount."
            )
        
        return data

    def create(self, validated_data):
        payment_mode_id = validated_data.pop('payment_mode_id')
        payment_mode = PaymentMode.objects.get(id=payment_mode_id)
        
        # Create the payment
        payment = PaymentIn.objects.create(
            **validated_data,
            payment_mode=payment_mode
        )

        # Update receivable amount
        receivable = payment.receivable
        receivable.amount -= payment.amount
        
        # If receivable is fully paid, delete it
        

        # Update sale status
        sale = payment.sale
        total_paid = PaymentIn.objects.filter(sale=sale).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        # Calculate total sale amount from items
        total_sale_amount = sum(
            item.product.sale_price * item.quantity
            for item in SaleItem.objects.filter(sale=sale)
        )

        # Update sale status based on payments
        if total_paid + Sale.objects.get(id=sale.id).total_amount >= total_sale_amount:
            sale.status = Sale.SaleStatus.PAID
        elif total_paid > 0:
            sale.status = Sale.SaleStatus.PARTIALLY_PAID
        else:
            sale.status = Sale.SaleStatus.UNPAID
        
        if receivable.amount <= 0:
            receivable.delete()
        else:
            receivable.save()

        sale.save()

        return payment

    def update(self, instance, validated_data):
        if 'payment_mode_id' in validated_data:
            payment_mode_id = validated_data.pop('payment_mode_id')
            payment_mode = PaymentMode.objects.get(id=payment_mode_id)
            instance.payment_mode = payment_mode

        # Get the old amount before update
        old_amount = instance.amount
        
        # Update the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Calculate the difference in amount
        amount_difference = instance.amount - old_amount

        # Update receivable amount
        receivable = instance.receivable
        receivable.amount -= amount_difference
        
        # If receivable is fully paid, delete it
        if receivable.amount <= 0:
            receivable.delete()
        else:
            receivable.save()

        # Update sale status
        sale = instance.sale
        total_paid = PaymentIn.objects.filter(sale=sale).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        # Calculate total sale amount from items
        total_sale_amount = sum(
            item.product.sale_price * item.quantity
            for item in SaleItem.objects.filter(sale=sale)
        )

        # Update sale status based on payments
        if total_paid >= total_sale_amount:
            sale.status = Sale.SaleStatus.PAID
        elif total_paid > 0:
            sale.status = Sale.SaleStatus.PARTIALLY_PAID
        else:
            sale.status = Sale.SaleStatus.UNPAID
        
        sale.save()
        instance.save()
        
        return instance 