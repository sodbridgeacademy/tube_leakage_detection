from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import UserProfileForm, UserRegisterForm, DatasetUploadForm
from .models import Profile, Dataset, Result

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler  
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split



# All views here!
def index(request):
    return redirect('login')


def about(request):
    return render(request, 'about.html')


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

            # Load the uploaded dataset
            dataset_path = dataset.file.path
            data = pd.read_csv(dataset_path)
            
            # Set the 'Date' column as the index
            data.set_index('Date', inplace=True)
            print(f'data deets => {data.shape}')

            # Generate a summary of the dataset
            data_head = data.head()
            data_description = data.describe()
            data_shape = data.shape

            context = {
                'form': form,
                'data_head': data_head,
                'data_description': data_description,
                'data_shape': data_shape,
            }
            return redirect('data_summary', dataset_id=dataset.id)
            #return render(request, 'data_summary.html', context)
    else:
        form = DatasetUploadForm()
    return render(request, 'upload_file.html', {'form': form})


@login_required
def data_summary_view(request, dataset_id):
    # Retrieve the dataset using the dataset_id parameter
    dataset = get_object_or_404(Dataset, id=dataset_id)

    # Load the uploaded dataset
    data = pd.read_csv(dataset.file.path)

    # Set the 'Date' column as the index
    data.set_index('Date', inplace=True)

    # Generate a summary of the dataset
    data_head = data.head()
    data_description = data.describe()
    data_shape = data.shape

    context = {
        'dataset': dataset,
        'data_head': data_head,
        'data_description': data_description,
        'data_shape': data_shape,
    }
    return render(request, 'data_summary.html', context)


@login_required
def perform_anomaly_detection(request, dataset_id):
    # Load the uploaded dataset
    #dataset = Dataset.objects.filter(user=request.user).latest('created_at')
    
    dataset = get_object_or_404(Dataset, id=dataset_id)
    dataset_path = dataset.file.path
    data = pd.read_csv(dataset_path)

    # Convert 'Date' column to datetime
    data['Date'] = pd.to_datetime(data['Date'])

    # Set the 'Date' column as the index
    data.set_index('Date', inplace=True)

    # Select input variables
    input_variables = [
        "COND WTR FLOW", "DEA&FEEDWATER TANK INLET WTR FLOW", "ECO OUTLET A FG O2",
        "ECO OUTLET B FG O2", "HOT SA A FLOW", "HOT SA B FLOW", "IDF-A INLET FG PRESS",
        "IDF-B INLET FG PRESS", "MAIN FEEDWATER FLOW", "Total Primary Air Flow",
        "GEN SIDE MW", "GEN SIDE FREQ"
    ]

    # Select the features
    features = input_variables

    # Extract the features
    extracted_features = data[features]

    # Cluster the data points using K-Means
    n_clusters = 2 
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    labels = kmeans.fit_predict(extracted_features)

    # Get the predicted anomalies; Train the isolation forest model
    xmodel = IsolationForest(n_estimators=100)
    xmodel.fit(extracted_features)

    # Calculate the anomaly scores for each data point
    anomaly_scores = xmodel.predict(extracted_features)
    print(f'ANOMALY SCORES => {anomaly_scores}, {anomaly_scores.shape}')

    # Select the data points with the highest anomaly scores
    anomalies = extracted_features[anomaly_scores==-1]
    anomalies_shape = anomalies.shape


    # Add the cluster labels to the extracted_features DataFrame
    extracted_features["LABEL"] = labels

    # Split the data into train/test sets
    X_train, X_test, y_train, y_test = train_test_split(
        extracted_features.drop(columns=["LABEL"]), labels, test_size=0.2, random_state=0
    )

    # Create an isolation forest model
    model = IsolationForest(random_state=0)

    # Fit the model to the train set
    model.fit(X_train)

    # Predict anomalies on the testing set
    anomaly_scores = model.predict(X_test)
    #print(f'ANOMALIES => {anomaly_scores}')

    # Select the data points with the highest anomaly scores
    anomalies = X_test[anomaly_scores==-1]

    # Convert anomaly scores to binary labels (1 for anomalies, 0 for normal)
    predicted_labels = [1 if score == -1 else 0 for score in anomaly_scores]

    # Calculate precision, recall, and F1-score
    precision = precision_score(y_test, predicted_labels)
    recall = recall_score(y_test, predicted_labels)
    f1 = f1_score(y_test, predicted_labels)

    p, r, f = f'{precision:.2}', f'{recall:.2}', f'{f1:.2}'
    sample_anomalies = anomalies.head(6)

    # Reset the index of sample_anomalies and convert the 'Date' column to a string
    sample_anomalies.reset_index(inplace=True)
    sample_anomalies['Date'] = sample_anomalies['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')


    # Convert the 'Date' column in sample_anomalies to a string
    #sample_anomalies['Date'] = sample_anomalies.index.strftime('%Y-%m-%d %H:%M:%S')

    list_sample_anomalies = list(sample_anomalies)
    
    print(f'sample anomalies original => {sample_anomalies}')
    print(f'sample anomalies columns list => {list_sample_anomalies}')
    
    # Extract the dates from the original dataset
    #anomaly_dates = data.loc[anomalies.index, "Date"]


    Result.objects.create(
            user=request.user,
            precision= p,
            recall= r,
            f1_score= f,
            dataset=dataset,
            anomalies_shape=anomalies_shape,
        )

    # Create a context dictionary with the results
    context = {
        'anomalies': anomalies,
        'precision': f'{precision:.2%}',
        'recall': f'{recall:.2%}',
        'f1_score': f'{f1:.2%}',
        'data_shape':len(anomaly_scores),
        #'anomalies': anomalies,
        'anomalies_shape':anomalies_shape,
        'sample_anomalies': sample_anomalies,
        'anomalies_head': sample_anomalies.head(),
        'anomalies_head_count':len(anomalies.head()),
        #'anomaly_dates': anomaly_dates
    }

    # Render a results page with the context
    return render(request, 'results.html', context)


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

