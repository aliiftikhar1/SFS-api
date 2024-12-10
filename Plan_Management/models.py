from django.db import models

from Utilities.Enums import PlanTypes, CurrencyUnits, PlanStatus, PlanDetailsTypes


class Plan(models.Model):
    name = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=25, choices=PlanTypes.choices, default=PlanTypes.MONTHLY_ANNUALLY)
    status = models.CharField(max_length=25, choices=PlanStatus.choices, default=PlanStatus.ACTIVE)


class PlanDetails(models.Model):
    pricing = models.IntegerField()
    points = models.IntegerField()
    timeline = models.CharField(max_length=25, choices=PlanDetailsTypes.choices, default=PlanDetailsTypes.MONTHLY)
    currency = models.CharField(max_length=1, choices=CurrencyUnits.choices, default=CurrencyUnits.DOLLAR)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True, related_name='details')
    duration = models.IntegerField(default=None, null=True, blank=True)


class Pricing(models.Model):
    cents_per_point = models.FloatField(default=0.0)
    points_per_sample = models.IntegerField(default=0)
    points_per_midi = models.IntegerField(default=0)
    points_per_preset = models.IntegerField(default=0)
    non_profits_licence = models.IntegerField(default=0)
    commercial_licence = models.IntegerField(default=0)
    unlimited_licence = models.IntegerField(default=0)
