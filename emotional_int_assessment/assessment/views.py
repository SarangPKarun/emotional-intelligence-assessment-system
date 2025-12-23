from django.shortcuts import render, redirect
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from .models import UserProfile, UserResponse, LocalEQAnalyzer
from .services import generate_scenario, generate_questions, interpret_eq, validate_response, eq_evaluation


def home(request):
    return render(request, 'assessment/home.html')

# def check(request):


#     analyzer = LocalEQAnalyzer()
#     evaluation = analyzer.evaluate(["I am very happy", "i will make a debate with him"], "female", age=30)
#     # sentiment = analyzer.analyze_sentiment("I am very happy")

#     return JsonResponse({
#         "evaluation": evaluation,
#         # "sentiment": sentiment
#     })


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

    que = [response.question for response in responses]
    ans = [response.answer for response in responses]
    eq_result = eq_evaluation(ans, user.gender, user.age)
    print(eq_result)

    context = {
        "profile": user,
        "eq_result": eq_result,
        "questions": que,
        "answers": ans,
    }

    # overall_score = 80

    # interpretation = interpret_eq(overall_score)

    # context = {
    #     "profile": user,
    #     "overall_score": 80,
    #     "feedback": interpretation["message"],
    #     "eq_level": interpretation["level"],
    #     "eq_color": interpretation["color"],
    #     "categories": {
    #         "Self-Awareness": 35, 
    #         "Emotional Resilience": 45, 
    #         "Conflict Resolution": 55, 
    #         "Empathy": 65, 
    #         "Social Skills": 75
    #     },
    #     "responses": responses
    # }

    return render(request, 'assessment/result.html', context)

    




