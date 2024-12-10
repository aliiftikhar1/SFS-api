from django.urls import path

from Plan_Management.Views import MonthlyAnnuallyPlanView, CustomPlanView, PlansView, PricingView

urlpatterns = [
    # Manage Plan
    path("view/", PlansView.as_view()),
    path("custom/", CustomPlanView.as_view()),
    path("monthly-yearly/", MonthlyAnnuallyPlanView.as_view()),

    # Manage Pricing
    path("pricing/", PricingView.as_view()),
]
