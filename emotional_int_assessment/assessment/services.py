from .models import LocalEQGenerator, LocalEQAnalyzer
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy

sentimentintensityanalyzer = SentimentIntensityAnalyzer()

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



STOPWORDS = {
    "ok", "okay", "yes", "no", "fine", "good", "bad",
    "nothing", "none", "idk", "dont know", "don't know",
    "na", "n/a"
}

def validate_meaningful_content(answer: str) -> tuple[bool, str]:
    text = answer.lower().strip()

    words = re.findall(r"\b[a-z]+\b", text)

    if not words:
        return False, "Response does not contain meaningful words"

    unique_words = set(words)
    if len(unique_words) < 3:
        return False, "Response is too repetitive or vague"

    if all(word in STOPWORDS for word in unique_words):
        return False, "Response lacks meaningful content"

    most_common_ratio = max(words.count(w) for w in unique_words) / len(words)
    if most_common_ratio > 0.6:
        return False, "Response is overly repetitive"

    if re.fullmatch(r"[a-z]{1,3}", text):
        return False, "Response appears invalid or random"

    return True, "OK"

# def validate_sentiment_coherence(answer: str) -> tuple[bool, str]:
#     scores = sentimentintensityanalyzer.polarity_scores(answer)
#     compound = scores["compound"] 

#     if abs(compound) < 0.1:
#         return False, "Response lacks emotional expression"

#     if scores["pos"] > 0.4 and scores["neg"] > 0.4:
#         return False, "Response shows conflicting emotions"

#     return True, "OK"


COMMON_VERBS = {
    "am", "is", "are", "was", "were", "be", "being", "been",
    "feel", "felt", "feels",
    "think", "thought",
    "handle", "handled",
    "manage", "managed",
    "experience", "experienced",
    "face", "faced",
    "deal", "dealt",
    "struggle", "struggled",
    "work", "worked"
}

CONNECTORS = {
    "because", "when", "while", "after", "before",
    "so", "but", "and", "although", "however"
}


nlp = spacy.load("en_core_web_sm")

def validate_sentence_coherence(answer: str) -> tuple[bool, str]:
    doc = nlp(answer)

    has_verb = any(token.pos_ == "VERB" for token in doc)
    has_subject = any(token.dep_ in ("nsubj", "nsubjpass") for token in doc)

    if not has_subject or not has_verb:
        return False, "Response lacks clear action or experience"

    return True, "OK"


def validate_response(answer: str):
    is_valid, msg = validate_length(answer)
    if not is_valid:
        return False, msg

    is_valid, msg = validate_meaningful_content(answer)
    if not is_valid:
        return False, msg

    is_valid, msg = validate_sentence_coherence(answer)
    if not is_valid:
        return False, msg
    
    # is_valid, msg = validate_sentiment_coherence(answer)
    # if not is_valid:
    #     return False, msg

    return True, "Valid"

def analyze_emotion(answer: str):
    scores = sentimentintensityanalyzer.polarity_scores(answer)
    compound = scores["compound"]

    if compound > 0.1:
        label = "positive"
    elif compound < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {
        "sentiment_label": label,
        "sentiment_score": compound,
        "emotion_intensity": abs(compound)
    }


eq_categories = {
    1: "Self-Awareness",
    2: "Emotional Resilience",
    3: "Conflict Resolution",
    4: "Empathy",
    5: "Social Skills",
}

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



def eq_evaluation(responses: list[str], gender: str, age: int):
    analyzer = LocalEQAnalyzer()
    evaluation = analyzer.evaluate(responses, gender, age)
    return evaluation
    