from django.db import models

# Create your models here.
from django.db import models

class PredictionLog(models.Model):
    task_id = models.UUIDField()
    url = models.URLField()
    prediction = models.CharField(max_length=20)
    confidence = models.FloatField()
    features = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.url} -> {self.prediction} ({self.confidence:.2f})"