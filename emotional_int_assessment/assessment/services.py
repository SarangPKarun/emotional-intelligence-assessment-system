from .models import LocalEQGenerator
generator = LocalEQGenerator()

def generate_scenario(user):
    """
    Calls the EQ generator class and returns scenario text
    """
    print("User profile:", user)
    user_profile = {
        "age": user.age,
        "gender": user.gender,
        "profession": user.profession
    }

    scenario = generator.generate_scenario(user_profile)

    return scenario

def generate_questions(scenario):
    """
    Calls the EQ generator class and returns questions in list 
    """
    print("User scenario:", scenario)

    questions = generator.generate_questions(scenario)

    return questions

def validate_length(answer: str) -> tuple[bool, str]:
    if not answer:
        print("Answer is empty")
        return False, "Answer is empty"

    if len(answer) < 15:
        print("Answer is too short")
        return False, "Answer is too short"

    if len(answer) > 500:
        print("Answer is too long")
        return False, "Answer is too long"

    if len(answer.split()) < 4:
        print("Answer lacks sufficient detail")
        return False, "Answer lacks sufficient detail"

    return True, "OK"


categories = [
            "Self-Awareness", 
            "Emotional Resilience", 
            "Conflict Resolution", 
            "Empathy", 
            "Social Skills"
        ]

def interpret_eq(score):
    if score < 40:
        return {
            "level": "Low EQ",
            "message": "Your EQ is currently low. Focus on emotional awareness.",
            "color": "red"
        }
    elif score < 70:
        return {
            "level": "Moderate EQ",
            "message": "You show moderate emotional intelligence.",
            "color": "yellow"
        }
    else:
        return {
            "level": "High EQ",
            "message": "You demonstrate strong emotional intelligence.",
            "color": "green"
        }



# import random
# from transformers import pipeline

# class AdvancedEQAssessmentModel:
#     def __init__(self):
#         # Initialize Hugging Face pipelines
#         # Using a distinct emotion model and a general sentiment model
#         try:
#             self.emotion_classifier = pipeline(
#                 "text-classification", 
#                 model="j-hartmann/emotion-english-distilroberta-base", 
#                 top_k=None
#             )
#             self.sentiment_analyzer = pipeline(
#                 "sentiment-analysis",
#                 model="distilbert-base-uncased-finetuned-sst-2-english"
#             )
#             self.model_loaded = True
#         except Exception as e:
#             print(f"Error loading models: {e}")
#             self.model_loaded = False

#     def generate_scenario(self, profession, age, gender):
#         """
#         Generates a profession-specific scenario.
#         """
#         scenarios = {
#             "default": "You are leading a team project that is falling behind schedule. One team member seems disengaged.",
#             "software engineer": "You are a Senior Developer. A critical bug is found in production just before the weekend. A junior developer pushed the code and feels terrible.",
#             "nurse": "You are a head nurse. A patient's family is very upset about the wait times and is raising their voice at your staff.",
#             "teacher": "You are a high school teacher. A usually bright student has stopped turning in homework and seems withdrawn.",
#             "manager": "You are a project manager. Two of your key stakeholders have conflicting requirements and neither is willing to compromise.",
#             "sales": "You are a sales executive. A long-term client is threatening to leave because of a mistake made by your support team."
#         }
        
#         key = profession.lower()
#         if key not in scenarios:
#             # Try partial match
#             for k in scenarios:
#                 if k in key:
#                     key = k
#                     break
#             else:
#                 key = "default"
                
#         base_scenario = scenarios[key]
#         return f"{base_scenario} How do you handle this situation?"

#     def generate_questions(self, scenario):
#         """
#         Generates reflective questions based on the scenario.
#         """
#         questions = [
#             "How would you approach the individual involved initially?",
#             "What emotions do you think they are feeling, and how would you address them?",
#             "How do you manage your own stress or frustration in this moment?",
#             "What is the ideal outcome you are striving for?"
#         ]
#         return questions

#     def analyze_responses(self, responses):
#         """
#         Analyzes a list of text responses for emotion and sentiment.
#         Returns aggregated scores.
#         """
#         if not self.model_loaded:
#             return {"error": "Models not loaded"}

#         total_emotions = {}
#         total_sentiment_score = 0
        
#         for response in responses:
#             # key: input text
#             # Emotion analysis
#             emotions = self.emotion_classifier(response)[0]
#             # Format: [{'label': 'joy', 'score': 0.9}, ...]
#             for emo in emotions:
#                 label = emo['label']
#                 score = emo['score']
#                 total_emotions[label] = total_emotions.get(label, 0) + score
            
#             # Sentiment analysis
#             sentiment = self.sentiment_analyzer(response)[0]
#             # Format: {'label': 'POSITIVE', 'score': 0.99}
#             s_val = sentiment['score'] if sentiment['label'] == 'POSITIVE' else -sentiment['score']
#             total_sentiment_score += s_val

#         # Normalize emotions
#         count = len(responses)
#         normalized_emotions = {k: v/count for k, v in total_emotions.items()}
#         avg_sentiment = total_sentiment_score / count

#         return {
#             "emotions": normalized_emotions,
#             "sentiment_score": avg_sentiment
#         }

#     def calculate_eq_score(self, analysis_result):
#         """
#         Maps emotion/sentiment analysis to EQ categories.
#         """
#         emotions = analysis_result.get("emotions", {})
#         sentiment = analysis_result.get("sentiment_score", 0)
        
#         # Categories mapping
#         # High Empathy: sadness, joy (sharing feelings), surprise (openness) ???
#         # Actually: 'joy' usually correlates with positive management. 'anger'/'disgust' negatively impacts.
#         # 'neutral' is good for regulation.
        
#         # Self-Awareness: ability to articulate feelings (this is hard to measure from text directly without specific content analysis, 
#         # but we can use balance of emotions).
        
#         # Mapping (Heuristic)
#         # 1. Emotional Resilience: Low 'anger', Low 'fear', High 'neutral' or controlled sentiment.
#         # 2. Empathy: Detection of 'sadness' or 'fear' in others? 
#         # Since we are analyzing the USER'S response, if they use 'joy' or positive language, they are likely constructive.
#         # If they use 'anger', it's bad.
        
#         negativity = emotions.get('anger', 0) + emotions.get('disgust', 0) + emotions.get('fear', 0)
#         positivity = emotions.get('joy', 0) + emotions.get('neutral', 0) # Neutral is capable/calm
        
#         # EQ Score 0-100
#         base_score = 70 # start average
        
#         # Adjust based on sentiment (-1 to 1)
#         base_score += sentiment * 20 
        
#         # Adjust based on emotion balance
#         base_score -= (negativity * 30)
#         base_score += (positivity * 10)
        
#         # Clamp
#         final_score = max(min(base_score, 100), 40)
        
#         # Category Breakdown
#         categories = {
#             "Self-Awareness": min(100, final_score + random.randint(-5, 5)),
#             "Self-Regulation": max(0, 100 - (negativity * 100)),
#             "Empathy": max(0, 50 + (positivity * 50)),
#             "Social Skills": max(0, 60 + (sentiment * 40)),
#             "Motivation": max(0, 70 + (emotions.get('joy', 0) * 50))
#         }
        
#         return {
#             "overall_score": int(final_score),
#             "categories": {k: int(v) for k, v in categories.items()},
#             "feedback": self._generate_feedback(final_score)
#         }

#     def _generate_feedback(self, score):
#         if score > 80:
#             return "Excellent EQ! You demonstrate high emotional intelligence, balancing empathy and regulation effectively."
#         elif score > 60:
#             return "Good EQ. You have a solid grasp of emotional dynamics but could improve on handling high-stress situations."
#         else:
#             return "Developing EQ. Focus on recognizing your triggers and practicing active listening."
