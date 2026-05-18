from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import analyze_url_task
from celery.result import AsyncResult
from django_ratelimit.decorators import ratelimit
from django_ratelimit.core import is_ratelimited


# Create your views here.
@api_view(['POST'])
@ratelimit(key='ip', rate='100/m', method='POST')
def submit_url(request):
    if is_ratelimited(request, group='predict', key='ip', rate='100/m', increment=True):
        return Response({'error': 'Rate limit exceeded. Max 100 requests per minute.'}, status=429)
    
    url = request.data.get('url')
    if not url:
        return Response({'error': 'url required'}, status=400)
    
    task = analyze_url_task.delay(url)
    return Response({'task_id': task.id}, status=202)

@api_view(['GET'])
def task_status(request, task_id):
    result = AsyncResult(task_id)
    if result.ready():
        return Response({
            'task_id': task_id,
            'status': 'completed',
            'result': result.result
        })
    else:
        return Response({
            'task_id': task_id,
            'status': result.status
        })