from django.urls import path
from transactions.views.payment_mode import PaymentModeListView, PaymentModeDetailView
from financials.views.expense_category import ExpenseCategoryListView, ExpenseCategoryDetailView
from financials.views.expense import ExpenseListView, ExpenseDetailView
from financials.views.payable import PayableListView, PayableDetailView
from financials.views.receivable import ReceivableListView, ReceivableDetailView
from financials.views.payment_in import PaymentInListView, PaymentInDetailView
from financials.views.payment_out import PaymentOutListView, PaymentOutDetailView

app_name = 'financials'

urlpatterns = [
    # Expense Category URLs
    path('stores/<uuid:store_id>/expense-categories/', ExpenseCategoryListView.as_view(), name='expense-category-list'),
    path('stores/<uuid:store_id>/expense-categories/<uuid:id>/', ExpenseCategoryDetailView.as_view(), name='expense-category-detail'),
    
    # Expense URLs
    path('stores/<uuid:store_id>/expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('stores/<uuid:store_id>/expenses/<uuid:id>/', ExpenseDetailView.as_view(), name='expense-detail'),
    
    # Payable URLs
    path('stores/<uuid:store_id>/payables/', PayableListView.as_view(), name='payable-list'),
    path('stores/<uuid:store_id>/payables/<uuid:id>/', PayableDetailView.as_view(), name='payable-detail'),
    
    # Receivable URLs
    path('stores/<uuid:store_id>/receivables/', ReceivableListView.as_view(), name='receivable-list'),
    path('stores/<uuid:store_id>/receivables/<uuid:id>/', ReceivableDetailView.as_view(), name='receivable-detail'),
    
    # Payment In URLs
    path('stores/<uuid:store_id>/payments-in/', PaymentInListView.as_view(), name='payment-in-list'),
    path('stores/<uuid:store_id>/payments-in/<uuid:id>/', PaymentInDetailView.as_view(), name='payment-in-detail'),
    
    # Payment Out URLs
    path('stores/<uuid:store_id>/payments-out/', PaymentOutListView.as_view(), name='payment-out-list'),
    path('stores/<uuid:store_id>/payments-out/<uuid:id>/', PaymentOutDetailView.as_view(), name='payment-out-detail'),
] 