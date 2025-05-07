from rest_framework import serializers
from django.db import models
from financials.models.payment_out import PaymentOut
from transactions.serializers.payment_mode import PaymentModeSerializer
from transactions.models.payment_mode import PaymentMode
from transactions.models.purchase import Purchase
from transactions.models.purchase_item import PurchaseItem


class PaymentOutSerializer(serializers.ModelSerializer):
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PaymentOut
        fields = [
            'id',
            'company',
            'payable',
            'purchase',
            'amount',
            'currency',
            'payment_mode',
            'payment_mode_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company': {'required': True},
            'payable': {'required': True},
            'purchase': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the payable and purchase belong to the same company
        and the payment amount is valid.
        """
        payable = data.get('payable')
        purchase = data.get('purchase')
        company = data.get('company')
        amount = data.get('amount')
        
        if payable and company and payable.company != company:
            raise serializers.ValidationError(
                "The selected payable does not belong to this company."
            )
            
        if purchase and company and purchase.company != company:
            raise serializers.ValidationError(
                "The selected purchase does not belong to this company."
            )

        if amount <= 0:
            raise serializers.ValidationError(
                "Payment amount must be greater than zero."
            )

        if amount > payable.amount:
            raise serializers.ValidationError(
                "Payment amount cannot exceed the payable amount."
            )
        
        return data

    def create(self, validated_data):
        payment_mode_id = validated_data.pop('payment_mode_id')
        payment_mode = PaymentMode.objects.get(id=payment_mode_id)
        
        # Create the payment
        payment = PaymentOut.objects.create(
            **validated_data,
            payment_mode=payment_mode
        )

        # Update payable amount
        payable = payment.payable
        payable.amount -= payment.amount
        
        # If payable is fully paid, delete it
        if payable.amount <= 0:
            payable.delete()
        else:
            payable.save()

        # Update purchase status
        purchase = payment.purchase
        total_paid = PaymentOut.objects.filter(purchase=purchase).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        # Calculate total purchase amount from items
        total_purchase_amount = sum(
            item.product.purchase_price * item.quantity
            for item in PurchaseItem.objects.filter(purchase=purchase)
        )

        # Update purchase status based on payments
        if total_paid >= total_purchase_amount:
            purchase.status = Purchase.PurchaseStatus.PAID
        elif total_paid > 0:
            purchase.status = Purchase.PurchaseStatus.PARTIALLY_PAID
        else:
            purchase.status = Purchase.PurchaseStatus.UNPAID
        
        purchase.save()

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

        # Update payable amount
        payable = instance.payable
        payable.amount -= amount_difference
        
        # If payable is fully paid, delete it
        if payable.amount <= 0:
            payable.delete()
        else:
            payable.save()

        # Update purchase status
        purchase = instance.purchase
        total_paid = PaymentOut.objects.filter(purchase=purchase).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        # Calculate total purchase amount from items
        total_purchase_amount = sum(
            item.product.purchase_price * item.quantity
            for item in PurchaseItem.objects.filter(purchase=purchase)
        )

        # Update purchase status based on payments
        if total_paid >= total_purchase_amount:
            purchase.status = Purchase.PurchaseStatus.PAID
        elif total_paid > 0:
            purchase.status = Purchase.PurchaseStatus.PARTIALLY_PAID
        else:
            purchase.status = Purchase.PurchaseStatus.UNPAID
        
        purchase.save()
        instance.save()
        
        return instance 