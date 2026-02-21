from django.db import models


class Plot(models.Model):
    json = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
