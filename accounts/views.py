from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import UserProfileForm, UserRegisterForm, DatasetUploadForm
from .models import Profile, Dataset


# All views here!
def index(request):
    return redirect('login')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
	profile = Profile.objects.filter(user=request.user)
	return render(request, 'dashboard.html')


@login_required(login_url='login')
def profile_view(request):
    user = request.user
    
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user.profile)
        print(f'deets: {form}')
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'update_profile.html', {'form': form})


@login_required
def upload_dataset_view(request):
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.user = request.user
            dataset.save()
            # Preprocess and run anomaly detection here
            return redirect('results')
    else:
        form = DatasetUploadForm()
    return render(request, 'upload_file.html', {'form': form})


@login_required
def results(request):
    # Retrieve and display anomaly detection results here
    return render(request, 'results.html')


@login_required(login_url='login')
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.user = request.user
            file.save()
            return redirect('convert', file_id=file.id)
    else:
        form = UploadFileForm()
    return render(request, 'upload_file.html', {'form': form})

