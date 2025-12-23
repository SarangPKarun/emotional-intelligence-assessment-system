from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import UserProfile, UserResponse
from .services import generate_scenario, generate_questions, interpret_eq, validate_response


def home(request):
    return render(request, 'assessment/home.html')


def assessment(request):
    if request.method == "POST":
        UserProfile.objects.all().delete()
        
        user = UserProfile.objects.create(
            age=request.POST.get("age"),
            gender=request.POST.get("gender"),
            profession=request.POST.get("profession"),
        )
    else:
        user = UserProfile.objects.first()
        if not user:
            return redirect("home")
    
    scenario = request.session.get("scenario")
    questions = request.session.get("questions")

    if not scenario or not questions:
        scenario = generate_scenario(user)
        questions = generate_questions(scenario)
        request.session["scenario"] = scenario
        request.session["questions"] = questions

    previous_responses = request.session.pop("previous_responses", {})
    validation_errors = request.session.pop("validation_errors", {})
    
    return render(request, 'assessment/assessment.html', {"scenario": scenario, "questions": questions, "profile": user, "previous_responses": previous_responses, "validation_errors": validation_errors})
        

def result(request):
    user = UserProfile.objects.first()
    if not user:
        return redirect("home")

    if request.method == "POST":
        questions = request.session.get("questions", [])

        errors = {}
        responses_data = {}

        for idx, question in enumerate(questions, start=1):
            answer = request.POST.get(f"response_{idx}", "").strip()

            responses_data[str(idx)] = answer

            is_valid, message = validate_response(answer)
            if not is_valid:
                errors[str(idx)] = message
        print(errors)
        if errors:
            request.session["validation_errors"] = errors
            request.session["previous_responses"] = responses_data
            return redirect("assessment")

        scenario = request.session.get("scenario")
        questions = request.session.get("questions", [])

        if not scenario or not questions:
            return redirect("assessment")   

        user.scenario = scenario
        user.save()

        UserResponse.objects.filter(user=user).delete()
        # UserResponse.objects.all().delete()

        for idx, question in enumerate(questions, start=1):
            answer = request.POST.get(f"response_{idx}").strip()

            UserResponse.objects.create(
                user=user,
                question=question,
                answer=answer
            )

        request.session.pop("scenario", None)
        request.session.pop("questions", None)
        request.session.pop("previous_responses", None)
        request.session.pop("validation_errors", None)

        return redirect("result")

    responses = UserResponse.objects.filter(user=user)

    if not user.scenario or not responses.exists():
        return redirect("assessment")

    overall_score = 80

    interpretation = interpret_eq(overall_score)

    context = {
        "profile": user,
        "overall_score": 80,
        "feedback": interpretation["message"],
        "eq_level": interpretation["level"],
        "eq_color": interpretation["color"],
        "categories": {
            "Self-Awareness": 35, 
            "Emotional Resilience": 45, 
            "Conflict Resolution": 55, 
            "Empathy": 65, 
            "Social Skills": 75
        },
        "responses": responses
    }

    return render(request, 'assessment/result.html', context)

    






#     from django.shortcuts import render, redirect
# from django.http import JsonResponse
# import os
# import sys

# # Add current directory to path to find eq_logic if needed, though relative import should work in app
# from .eq_logic import AdvancedEQAssessmentModel

# # Initialize model once (globally)
# try:
#     model = AdvancedEQAssessmentModel()
# except Exception:
#     model = None # Handle optional load failure

# def landing(request):
#     return render(request, 'assessment/landing.html')

# def start_assessment(request):
#     if request.method == 'POST':
#         age = request.POST.get('age')
#         gender = request.POST.get('gender')
#         profession = request.POST.get('profession')
        
#         request.session['user_info'] = {
#             'age': age,
#             'gender': gender,
#             'profession': profession
#         }
        
#         if model:
#             scenario = model.generate_scenario(profession, age, gender)
#             questions = model.generate_questions(scenario)
#         else:
#             scenario = "Error loading AI model."
#             questions = []
        
#         request.session['scenario'] = scenario
#         request.session['questions'] = questions
        
#         return redirect('assessment')
#     return redirect('landing')

# def assessment(request):
#     scenario = request.session.get('scenario')
#     questions = request.session.get('questions')
#     if not scenario:
#         return redirect('landing')
#     return render(request, 'assessment/assessment.html', {'scenario': scenario, 'questions': questions})

# def submit_assessment(request):
#     if request.method == 'POST':
#         questions = request.session.get('questions', [])
#         responses = []
#         for i in range(1, len(questions) + 1):
#             responses.append(request.POST.get(f'response_{i}', ''))
        
#         if model:
#             analysis = model.analyze_responses(responses)
#             result = model.calculate_eq_score(analysis)
#         else:
#             result = {}
        
#         request.session['result'] = result
#         return redirect('result')
#     return redirect('assessment')

# def result(request):
#     result = request.session.get('result')
#     if not result:
#         return redirect('landing')
#     return render(request, 'assessment/result.html', result)
