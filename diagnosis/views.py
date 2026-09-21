from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ml.predictor import predict_disease
from .models import TreatmentRecommendation
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView


@csrf_exempt
def diagnose(request):
    if request.method != "POST" or "image" not in request.FILES:
        return JsonResponse(
            {"error": "Отправьте изображение методом POST, поле 'image'"},
            status=400
        )

    image_file = request.FILES["image"]
    result = predict_disease(image_file)

    try:
        recommendation = TreatmentRecommendation.objects.get(
            class_name=result["class_name"]
        )
        treatment_data = {
            "disease_name": recommendation.disease_display_name,
            "description": recommendation.description,
            "treatment": recommendation.treatment,
            "duration": recommendation.treatment_duration,
        }
    except TreatmentRecommendation.DoesNotExist:
        treatment_data = {"error": "Рекомендация для этого класса ещё не добавлена в базу"}

    return JsonResponse({
        "class_name": result["class_name"],
        "confidence": result["confidence"],
        **treatment_data
    })

def home(request):
    return render(request, "diagnosis/home.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    form.fields["username"].label = "Имя пользователя"
    form.fields["username"].help_text = ""

    form.fields["password1"].label = "Пароль"
    form.fields["password1"].help_text = ""

    form.fields["password2"].label = "Подтверждение пароля"
    form.fields["password2"].help_text = ""

    return render(request, "diagnosis/register.html", {"form": form})


@login_required
def diagnose_page(request):
    return render(request, "diagnosis/diagnose.html")

class CustomLoginView(LoginView):
    template_name = "diagnosis/login.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["username"].label = "Имя пользователя"
        form.fields["password"].label = "Пароль"
        return form