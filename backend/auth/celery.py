from __future__ import absolute_import
import os
from celery import Celery

def make_celery():
    
    # Set default Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth.settings')

    app = Celery('auth')
    app.config_from_object('django.conf:settings', namespace='CELERY')

    # Explicit Redis configuration
    app.conf.update(
        broker_url='redis://redis:6379/0',
        result_backend='redis://redis:6379/0',
        broker_transport_options={'visibility_timeout': 3600},
        task_default_queue='default',
        task_queues={
            'default': {'exchange': 'default'},
            'text-processor': {'exchange': 'text-processor'},
            
        },
        task_routes={
            'api.uploads.tasks.process_text': {'queue': 'text-processor'},
            
        },
        broker_connection_retry_on_startup=True
    )
    # Discover tasks automatically
    app.autodiscover_tasks()

    return app

app = make_celery()
