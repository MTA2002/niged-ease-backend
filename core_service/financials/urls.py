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
    path('expense-categories/', ExpenseCategoryListView.as_view(), name='expense-category-list'),
    path('expense-categories/<uuid:id>/', ExpenseCategoryDetailView.as_view(), name='expense-category-detail'),
    
    # Expense URLs
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('expenses/<uuid:id>/', ExpenseDetailView.as_view(), name='expense-detail'),
    
    # Payable URLs
    path('payables/', PayableListView.as_view(), name='payable-list'),
    path('payables/<uuid:id>/', PayableDetailView.as_view(), name='payable-detail'),
    
    # Receivable URLs
    path('receivables/', ReceivableListView.as_view(), name='receivable-list'),
    path('receivables/<uuid:id>/', ReceivableDetailView.as_view(), name='receivable-detail'),
    
    # Payment In URLs
    path('payments-in/', PaymentInListView.as_view(), name='payment-in-list'),
    path('payments-in/<uuid:id>/', PaymentInDetailView.as_view(), name='payment-in-detail'),
    
    # Payment Out URLs
    path('payments-out/', PaymentOutListView.as_view(), name='payment-out-list'),
    path('payments-out/<uuid:id>/', PaymentOutDetailView.as_view(), name='payment-out-detail'),
] 