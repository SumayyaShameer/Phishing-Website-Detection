from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .forms import RegisterForm
from .models import LoginActivity
import os
import joblib
from django.conf import settings

MODEL_PATH = os.path.join(
    settings.BASE_DIR,
    'login_monitor',
    'ml_model',
    'login_model.pkl'
)

ml_model = joblib.load(MODEL_PATH)

def home(request):
    return render(request, 'login_monitor/home.html')


def register_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Registration successful. Please login.'
            )

            return redirect('login')

    else:
        form = RegisterForm()

    return render(
        request,
        'login_monitor/register.html',
        {'form': form}
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        current_time = timezone.localtime()

        login_hour = current_time.hour
        day_of_week = current_time.weekday()

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # ------------------------------------------
        # LOGIN STATUS FEATURE
        # ------------------------------------------

        if user is not None:
            login_status_value = 1
        else:
            login_status_value = 0


        # ------------------------------------------
        # LOGIN FREQUENCY FEATURE
        # Count recent attempts for this username
        # ------------------------------------------

        login_frequency = (
            LoginActivity.objects.filter(
                username_attempted=username
            ).count() + 1
        )

        # Limit to same range used during training
        login_frequency = min(
            login_frequency,
            10
        )


        # ------------------------------------------
        # IP RISK FEATURE
        # 0 = known/local network
        # 1 = unknown/unusual network
        # ------------------------------------------

        ip_address = request.META.get(
            'REMOTE_ADDR'
        )

        if ip_address in [
            '127.0.0.1',
            '::1'
        ]:
            ip_risk = 0
        else:
            ip_risk = 1


        # ------------------------------------------
        # MACHINE LEARNING PREDICTION
        # ------------------------------------------

        features = [[
            login_hour,
            day_of_week,
            login_frequency,
            login_status_value,
            ip_risk
        ]]

        ml_prediction = ml_model.predict(
            features
        )[0]


        if ml_prediction == 1:
            prediction = 'Suspicious'
        else:
            prediction = 'Normal'


        # ------------------------------------------
        # SUCCESSFUL AUTHENTICATION
        # ------------------------------------------

        if user is not None:

            LoginActivity.objects.create(
                user=user,
                username_attempted=username,
                login_hour=login_hour,
                day_of_week=day_of_week,
                login_status='Success',
                ip_address=ip_address,
                login_frequency=login_frequency,
                prediction=prediction
            )

            login(
                request,
                user
            )


            if prediction == 'Suspicious':

                messages.warning(
                    request,
                    'Security Alert: This login activity '
                    'has been classified as suspicious.'
                )

            return redirect(
                'dashboard'
            )


        # ------------------------------------------
        # FAILED AUTHENTICATION
        # ------------------------------------------

        else:

            LoginActivity.objects.create(
                username_attempted=username,
                login_hour=login_hour,
                day_of_week=day_of_week,
                login_status='Failed',
                ip_address=ip_address,
                login_frequency=login_frequency,
                prediction=prediction
            )

            messages.error(
                request,
                'Invalid username or password.'
            )


    return render(
        request,
        'login_monitor/login.html'
    )

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        current_time = timezone.localtime()

        login_hour = current_time.hour
        day_of_week = current_time.weekday()

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            LoginActivity.objects.create(
                user=user,
                username_attempted=username,
                login_hour=login_hour,
                day_of_week=day_of_week,
                login_status='Success',
                login_frequency=1,
                prediction='Normal'
            )

            return redirect('dashboard')

        else:

            LoginActivity.objects.create(
                username_attempted=username,
                login_hour=login_hour,
                day_of_week=day_of_week,
                login_status='Failed',
                login_frequency=1,
                prediction='Suspicious'
            )

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(
        request,
        'login_monitor/login.html'
    )


# @login_required
# def dashboard(request):

#     activities = LoginActivity.objects.filter(
#         user=request.user
#     ).order_by('-login_time')

#     return render(
#         request,
#         'login_monitor/dashboard.html',
#         {'activities': activities}
#     )

@login_required
def dashboard(request):

    activities = LoginActivity.objects.filter(
        user=request.user
    ).order_by('-login_time')

    return render(
        request,
        'login_monitor/dashboard.html',
        {
            'activities': activities
        }
    )

@login_required
def analyze_login(request):

    result = None

    if request.method == 'POST':

        login_hour = int(
            request.POST.get('login_hour')
        )

        day_of_week = int(
            request.POST.get('day_of_week')
        )

        login_frequency = int(
            request.POST.get('login_frequency')
        )

        login_status = int(
            request.POST.get('login_status')
        )

        ip_risk = int(
            request.POST.get('ip_risk')
        )

        # ------------------------------------------
        # MACHINE LEARNING PREDICTION
        # ------------------------------------------

        features = [[
            login_hour,
            day_of_week,
            login_frequency,
            login_status,
            ip_risk
        ]]

        prediction_value = ml_model.predict(
            features
        )[0]

        if prediction_value == 1:
            result = 'Suspicious'
        else:
            result = 'Normal'


        # ------------------------------------------
        # SAVE ANALYSIS RESULT TO DATABASE
        # ------------------------------------------

        ip_address = request.META.get(
            'REMOTE_ADDR'
        )

        LoginActivity.objects.create(
            user=request.user,
            username_attempted=request.user.username,
            login_hour=login_hour,
            day_of_week=day_of_week,
            login_status=(
                'Success'
                if login_status == 1
                else 'Failed'
            ),
            ip_address=ip_address,
            login_frequency=login_frequency,
            prediction=result
        )


    return render(
        request,
        'login_monitor/analyze_login.html',
        {
            'result': result
        }
    )


def logout_view(request):

    logout(request)

    return redirect('home')