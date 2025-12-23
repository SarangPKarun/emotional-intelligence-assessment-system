from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from huggingface_hub import InferenceClient
from django.conf import settings

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

    sentiment = models.CharField(max_length=20, null=True, blank=True)
    emotion_score = models.FloatField(null=True, blank=True)

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
                    "Rules:\n"
                    "- Questions must encourage self-reflection\n"
                    "- Focus on emotional awareness, motivation, conflict handling, and resilience\n"
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
