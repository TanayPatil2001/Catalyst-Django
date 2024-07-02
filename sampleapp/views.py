from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from django.contrib import messages
from .forms import CustomUserCreationForm,LargeFileForm
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
import pandas as pd
from django.core.management.base import BaseCommand
import uuid
from django.views.decorators.csrf import csrf_exempt
import threading
from functools import wraps

global current_user_name
current_user_name = None


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
    global current_user_name
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            current_user_name = user.username  # Store the username globally
            return redirect('base')
        else:
            print("Invalid form")
            print(form.errors)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    global current_user_name
    current_user_name = None
    return redirect('custom_login')

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        global current_user_name
        if not current_user_name:
            return redirect('custom_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def base(r):
    return render(r,'base.html')

# ==============================================================================
@login_required
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
df = None 
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

            if len(uploads[upload_id]['chunks']) == total_chunks:
                final_file_content = b''
                for i in range(total_chunks):
                    final_file_content += uploads[upload_id]['chunks'][i]

                
                global df 
                with df_lock:
                    try:
                        from io import BytesIO
                        df = pd.read_csv(BytesIO(final_file_content))
                        print(df.head())
                    except Exception as e:
                        print(f"Error reading CSV: {e}")

                del uploads[upload_id]['chunks']
                del request.session['upload_id']

        return JsonResponse({'message': 'Chunk uploaded successfully'})
    print("file upload horaha")

    return JsonResponse({'message': 'Method not allowed'}, status=405)

# ===========================================================================

@login_required
def query_builder(request):
        if df is None:
            print("DataFrame is None. Please upload data.")
            return redirect('upload_file')
        return render(request, 'query_builder.html')

 # =================================================================

@login_required
def user_list(request):
    users = User.objects.all()  # Fetch all registered users
    return render(request, 'user_list.html', {'users': users})
# ================================================================================
def count_records(request):
    global df
    if request.method == 'GET':
        search_name = request.GET.get('name', '')
        search_domain = request.GET.get('domain', '')
        search_country = request.GET.get('country', '')
        search_year = request.GET.get('year_founded', '')
        search_industry = request.GET.get('industry', '')
        if df is None:
            print("DataFrame is None. Please upload data.")
            return JsonResponse({'count': 0})  
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

        num = filtered_data.shape[0]  
        return JsonResponse({'count': num})
    elif request.method == 'POST':
        pass
    return JsonResponse({'error': 'Method not allowed'}, status=405)
