from rest_framework import serializers
from reports.models import (
    Report, 
    SalesReport, 
    InventoryReport, 
    FinancialReport, 
    CustomerReport, 
    ProductPerformanceReport,
    ProfitReport,
    RevenueReport
)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class SalesReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    
    class Meta:
        model = SalesReport
        fields = '__all__'


class InventoryReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    
    class Meta:
        model = InventoryReport
        fields = '__all__'


class FinancialReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    
    class Meta:
        model = FinancialReport
        fields = '__all__'


class CustomerReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    
    class Meta:
        model = CustomerReport
        fields = '__all__'


class ProductPerformanceReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    
    class Meta:
        model = ProductPerformanceReport
        fields = '__all__'


class ProfitReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    
    class Meta:
        model = ProfitReport
        fields = '__all__'


class RevenueReportSerializer(serializers.ModelSerializer):
    report = ReportSerializer()
    
    class Meta:
        model = RevenueReport
        fields = '__all__' 