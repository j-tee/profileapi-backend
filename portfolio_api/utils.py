"""
Custom utilities for the Portfolio API
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats error responses consistently
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response format
        custom_response_data = {
            'message': None,
            'errors': None,
            'status': response.status_code,
            'timestamp': datetime.now().isoformat()
        }

        # Extract error message
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                custom_response_data['message'] = 'An error occurred'
                custom_response_data['errors'] = response.data
        else:
            custom_response_data['message'] = str(response.data)

        response.data = custom_response_data

    return response


def get_upload_path(instance, filename, folder):
    """
    Generate upload path for files
    """
    import os
    from django.utils.text import slugify
    
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.__class__.__name__)}_{instance.id}.{ext}"
    return os.path.join(folder, filename)
