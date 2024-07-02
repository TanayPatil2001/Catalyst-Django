from django.db import models

class LargeFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class file_data(models.Model):
    id_1 = models.BigIntegerField(default=0,null=True)
    name = models.CharField(max_length=200, null=True)
    domain = models.CharField(max_length=200, null=True)
    year_founded = models.FloatField(null=True)
    industry = models.CharField(max_length=500, null=True)
    size_range = models.CharField(max_length=100, null=True)
    locality = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    linkedin_url = models.CharField(max_length=300, null=True)
    current_employee_estimate = models.IntegerField(null=True)
    total_employee_estimate = models.IntegerField(null=True)