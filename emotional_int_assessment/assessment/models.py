from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from huggingface_hub import InferenceClient
from django.conf import settings
from collections import defaultdict


class UserProfile(models.Model):
    age = models.PositiveIntegerField(validators=[MinValueValidator(10), MaxValueValidator(100)], null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    scenario = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 🔥 Ensure only ONE profile exists
        if not self.pk:
            UserProfile.objects.all().delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.profession} | {self.age} | {self.gender}"


class UserResponse(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="responses"
    )
    question = models.TextField()
    answer = models.TextField()

    # sentiment = models.CharField(max_length=20, null=True, blank=True)
    # sentiment_label = models.CharField(max_length=10, null=True, blank=True)
    # sentiment_score = models.FloatField(null=True, blank=True)
    # dominant_emotion = models.CharField(max_length=10, null=True, blank=True)
    # emotion_intensity = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response by User {self.user.id}"


class LocalEQGenerator:
    def __init__(self):
        print("Initializing EQ scenario generator (HF API)...")

        self.client = InferenceClient(
            model="meta-llama/Llama-3.1-8B-Instruct",
            token=settings.HF_TOKEN
        )

        print("EQ generator ready.")

    def generate_scenario(self, user_profile: dict) -> str:
        """
        Generates ONLY a professional workplace scenario.
        No advice. No solutions. No dialogue.
        """

        age = user_profile.get("age", "unknown")
        gender = user_profile.get("gender", "unknown")
        profession = user_profile.get("profession", "professional")

        messages = [
            {
                "role": "system",
                "content": "You are a professional workplace scenario generator."
            },
            {
                "role": "user",
                "content": (
                    f"Create a short professional workplace scenario for a {age}-year-old "
                    f"{gender} working as a {profession}.\n\n"
                    "Rules:\n"
                    "- Start with 'You are'\n"
                    "- Do NOT mention age, gender, or personal identity\n"
                    "- Describe only the situation\n"
                    "- Include pressure, conflict, or emotional stress\n"
                    "- Do NOT give advice\n"
                    "- Do NOT suggest actions or solutions\n"
                    "- Do NOT include dialogue\n"
                    "- Maximum 3–4 sentences\n\n"
                    "Scenario:"
                )
            }
        ]

        response = self.client.chat.completions.create(
            messages=messages,
            max_tokens=120,
            temperature=0.6,
            top_p=0.9
        )

        scenario = response.choices[0].message.content.strip()
        return scenario

    
    def generate_questions(self, scenario: str) -> list[str]:
        """
        Generates 5 contextual reflective questions
        focusing on emotional processing, motivation,
        conflict handling, and resilience.
        """

        messages = [
            {
                "role": "system",
                "content": "You generate reflective emotional intelligence assessment questions."
            },
            {
                "role": "user",
                "content": (
                    "Based on the following workplace scenario, generate exactly 5 "
                    "open-ended reflective questions.\n\n"
                    f"Scenario:\n{scenario}\n\n"
                    "Each question must focus on the following EQ dimensions IN ORDER:\n"
                    "1. Self-awareness (recognizing own emotions)\n"
                    "2. Emotional resilience (handling stress and pressure)\n"
                    "3. Conflict resolution (handling disagreements)\n"
                    "4. Empathy (understanding others' emotions)\n"
                    "5. Social skills (communication and teamwork)\n\n"
                    "Rules:\n"
                    "- Each question must clearly align with its assigned EQ dimension\n"
                    "- Encourage self-reflection\n"
                    "- Do NOT provide advice or guidance\n"
                    "- Do NOT include answers or examples\n"
                    "- Do NOT include multiple choice options\n"
                    "- Number questions from 1 to 5\n"
                    "- Use professional and neutral tone\n\n"
                    "Questions:"
                )
            }
        ]

        response = self.client.chat.completions.create(
            messages=messages,
            max_tokens=180,
            temperature=0.6,
            top_p=0.9
        )

        print(response)

        raw_output = response.choices[0].message.content.strip()

        questions = []
        for line in raw_output.split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                questions.append(line.split(".", 1)[1].strip())

        return questions


class LocalEQAnalyzer:
    """
    Handles:
    - Emotion & sentiment analysis
    - Emotional intensity computation
    - EQ category scoring
    - Overall EQ aggregation
    - Result interpretation
    """

    def __init__(self):
        print("Initializing EQ analysis engine (HF API)...")

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=settings.HF_TOKEN,
        )

        self.eq_categories = {
            1: "Self-Awareness",
            2: "Emotional Resilience",
            3: "Conflict Resolution",
            4: "Empathy",
            5: "Social Skills",
        }

        print("EQ analyzer ready.")


    def analyze_emotion(self, text: str) -> dict:
        """
        Uses HF emotion model to detect dominant emotion and emotional intensity.
        """

        result = self.client.text_classification(
            text,
            model="j-hartmann/emotion-english-distilroberta-base",
        )

        dominant = max(result, key=lambda x: x["score"])

        return {
            "dominant_emotion": dominant["label"],
            "emotion_intensity": dominant["score"],  
            "emotion_distribution": result,
        }

    def analyze_sentiment(self, text: str) -> dict:
        """
        Uses HF sentiment model to detect polarity.
        """

        result = self.client.text_classification(
            text,
            model="tabularisai/multilingual-sentiment-analysis",
        )
        print("analyze_sentiment result: ", result)
        sentiment = result[0]

        return {
            "sentiment_label": sentiment["label"],      
            "sentiment_confidence": sentiment["score"], 
        }

    def analyze_response(self, text: str) -> dict:
        """
        Runs emotion + sentiment analysis together.
        """

        emotion = self.analyze_emotion(text)
        sentiment = self.analyze_sentiment(text)

        return {
            **emotion,
            **sentiment,
        }

    def compute_category_score(
        self,
        sentiment_label: str,
        emotion_intensity: float,
        gender: str | None = None,
        age: int | None = None,
    ) -> int:


        base = 50  

        if sentiment_label == "positive":
            base += 15
        elif sentiment_label == "negative":
            base -= 10

        base += emotion_intensity * 30  # max +30

        if gender:
            g_lower = gender.lower()
            if g_lower == "female":
                base += 2
            elif g_lower == "male":
                base += 0  
            elif g_lower == "non-binary":
                base += 1

        if age:
            try:
                age_val = int(age)
                if age_val > 50:
                    base += 5
                elif age_val > 30:
                    base += 2
            except (ValueError, TypeError):
                pass

        return max(0, min(100, round(base)))


    def aggregate_eq_scores(self, responses: list, gender: str | None, age: int | None = None):
        """
        responses: list of dicts with analysis data
        """

        category_scores = defaultdict(list)

        for idx, r in enumerate(responses, start=1):
            category = self.eq_categories.get(idx)
            if not category:
                continue

            score = self.compute_category_score(
                sentiment_label=r["sentiment_label"],
                emotion_intensity=r["emotion_intensity"],
                gender=gender,
                age=age,
            )

            category_scores[category].append(score)

        return {
            cat: round(sum(scores) / len(scores))
            for cat, scores in category_scores.items()
        }


    def compute_overall_eq(self, category_scores: dict) -> int:
        if not category_scores:
            return 0
        return round(sum(category_scores.values()) / len(category_scores))


    def interpret_eq(self, overall_score: int) -> dict:
        if overall_score < 40:
            return {
                "level": "Low EQ",
                "message": "You may find it challenging to recognize and regulate emotions under pressure.",
                "color": "red",
            }
        elif overall_score < 70:
            return {
                "level": "Average EQ",
                "message": "You demonstrate reasonable emotional awareness and adaptability.",
                "color": "orange",
            }
        else:
            return {
                "level": "High EQ",
                "message": "You show strong emotional intelligence and emotional resilience.",
                "color": "green",
            }


    def evaluate(self, answers: list[str], gender: str | None = None, age: int | None = None) -> dict:
        """
        answers: list of user responses in question order
        """

        analyzed = [self.analyze_response(a) for a in answers]

        category_scores = self.aggregate_eq_scores(analyzed, gender, age)
        overall_eq = self.compute_overall_eq(category_scores)
        interpretation = self.interpret_eq(overall_eq)

        return {
            "overall_eq": overall_eq,
            "eq_level": interpretation["level"],
            "feedback": interpretation["message"],
            "eq_color": interpretation["color"],
            "category_scores": category_scores,
            "responses_analysis": analyzed,  
        }
