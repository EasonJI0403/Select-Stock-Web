from django.db import models
import pandas as pd
from datetime import date
from fugle_marketdata import RestClient

class Stock(models.Model):
    date = models.DateField(default=date.today)
    open_price = models.FloatField(default=0.0)
    high_price = models.FloatField(default=0.0)
    low_price = models.FloatField(default=0.0)
    close_price = models.FloatField(default=0.0)
    volume = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.close_price}"

