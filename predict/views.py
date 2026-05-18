from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import analyze_url_task
from celery.result import AsyncResult

# Create your views here.
@api_view(['POST'])
def submit_url(request):
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