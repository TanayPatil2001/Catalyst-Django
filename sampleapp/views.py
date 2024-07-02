from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserCreationForm
from django.contrib.auth import logout, login
from django.contrib import messages
from .forms import CustomUserCreationForm,LargeFileForm, FileDataForm, LargeFile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from .models import LargeFile, file_data
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import pandas as pd
import time
from sqlalchemy import create_engine
import csv
import os
from django.core.management.base import BaseCommand
import uuid
from django.views.decorators.csrf import csrf_exempt
import threading



def base(r):
    return render(r,'base.html')
# =======================================================================
def register(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            return redirect('custom_login')
    else:
        f = CustomUserCreationForm()
    return render(request, 'register.html', {'form': f})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print("login horaha")
            return redirect('base')
        else:
            print("Invalid form")
            print(form.errors)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('custom_login')

# ==============================================================================
def upload_file(request):
    if request.method == 'POST':
        form = LargeFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = LargeFileForm()
    return render(request, 'upload-file.html', {'form': form})

uploads = {}
uploads_lock = threading.Lock()
df = None #  Global variable to store the DataFrame
df_lock = threading.Lock()
@csrf_exempt
def upload_chunk(request):
    if request.method == 'POST':
        chunk = request.FILES['file']
        chunk_number = int(request.POST['chunk'])
        total_chunks = int(request.POST['total_chunks'])
        original_filename = request.POST['filename']

        with uploads_lock:
            upload_id = request.session.get('upload_id', None)
            if not upload_id:
                upload_id = str(uuid.uuid4())
                request.session['upload_id'] = upload_id
                uploads[upload_id] = {
                    'original_filename': original_filename,
                    'total_chunks': total_chunks,
                    'chunks': {}
                }

            uploads[upload_id]['chunks'][chunk_number] = chunk.read()

            # Check if all chunks are uploaded
            if len(uploads[upload_id]['chunks']) == total_chunks:
                # Reassemble the file
                final_file_content = b''
                for i in range(total_chunks):
                    final_file_content += uploads[upload_id]['chunks'][i]

                # Convert the file content to a pandas DataFrame
                global df  # Add this line to ensure df is recognized as a global variable
                with df_lock:
                    try:
                        from io import BytesIO
                        df = pd.read_csv(BytesIO(final_file_content))
                        print(df.head())
                    except Exception as e:
                        print(f"Error reading CSV: {e}")

                # Optionally, remove the chunk data to save memory
                del uploads[upload_id]['chunks']
                del request.session['upload_id']

        return JsonResponse({'message': 'Chunk uploaded successfully'})
    print("file upload horaha")

    return JsonResponse({'message': 'Method not allowed'}, status=405)

# ===========================================================================

def query_builder(request):
        if df is None:
            print("DataFrame is None. Please upload data.")
            return redirect('upload_file')
        return render(request, 'query_builder.html')

 # =================================================================

def user_list(request):
    users = User.objects.all()  # Fetch all registered users
    return render(request, 'user_list.html', {'users': users})
# ================================================================================
def count_records(request):
    global df
    if request.method == 'GET':
        # Fetch parameters from request
        search_name = request.GET.get('name', '')
        search_domain = request.GET.get('domain', '')
        search_country = request.GET.get('country', '')
        search_year = request.GET.get('year_founded', '')
        search_industry = request.GET.get('industry', '')
        # Check if df is None
        if df is None:
            print("DataFrame is None. Please upload data.")
            return JsonResponse({'count': 0})  # Return count as 0 or handle differently
        # Example filtering assuming df is your DataFrame
        filtered_data = df
        if search_country:
            search_year = int(search_year)
            filtered_data = df[
                (df['name'] == search_name) &
                (df['domain'] == search_domain) &
                (df['country'] == search_country) &
                (df['year founded'] == search_year) &
                (df['industry'] == search_industry)
            ]
        # Calculate number of records
        num = filtered_data.shape[0]  # Adjust as per your DataFrame structure
        return JsonResponse({'count': num})
    elif request.method == 'POST':
        # Handle POST method if necessary
        pass
    # Handle other cases or errors
    return JsonResponse({'error': 'Method not allowed'}, status=405)