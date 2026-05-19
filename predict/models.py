from django.db import models

class PredictionLog(models.Model):
    task_id = models.UUIDField()
    url = models.URLField()
    prediction = models.CharField(max_length=20)
    confidence = models.FloatField()
    features = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def domain_age_days(self):
        return self.features.get('domain_age_days', 'N/A')

    @property
    def ssl_valid(self):
        return self.features.get('ssl_valid', 'N/A')

    @property
    def using_shortener(self):
        return self.features.get('using_shortener', 'N/A')
    
    @property
    def url_length(self):
        return self.features.get('url_length', 'N/A')
    
    @property
    def num_subdomains(self):
        return self.features.get('num_subdomains', 'N/A')
    
    @property
    def contains_keyword(self):
        return self.features.get('contains_keyword', 'N/A')
    
    @property
    def has_ip(self):
        return self.features.get('has_ip', 'N/A')
    

    def __str__(self):
        return f"{self.url} -> {self.prediction} ({self.confidence:.2f})"