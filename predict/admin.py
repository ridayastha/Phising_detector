from django.contrib import admin
from .models import PredictionLog

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('url', 'prediction', 'confidence','domain_age_days','ssl_valid','using_shortener','url_length', 'num_subdomains', 'contains_keyword', 'has_ip', 'created_at')
    list_filter = ('prediction', 'created_at')
    search_fields = ('url', 'task_id')
    readonly_fields = ('task_id', 'url', 'prediction', 'confidence', 'features', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False