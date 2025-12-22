from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from . import EQAssessmentModel

def home(request):
    return render(request, 'assessment/home.html')

questions = [
    "How would you approach the individual involved initially?",
    "What emotions do you think they are feeling, and how would you address them?",
    "How do you manage your own stress or frustration in this moment?",
    "What is the ideal outcome you are striving for?",
    "What do you do if negative thoughts comes in mind?"
]

profile = {
    "age": 23,
    "gender": "Male",
    "profession": "Software Engineer"
}

def assessment(request):
    scenario = "You are leading a team under a tight deadline when a conflict arises between two members..."

    return render(request, 'assessment/assessment.html', {"scenario": scenario, "questions": questions, "profile": profile})

def result(request):
    interpretation = EQAssessmentModel.interpret_eq(80)
    print(interpretation)

    context = {
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
        }
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
