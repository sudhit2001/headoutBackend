from django.db import models

# User model to track scores
class User(models.Model):
    username = models.CharField(max_length=255, unique=True, null=False)
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.username} - Correct: {self.correct_answers}, Incorrect: {self.incorrect_answers}"
