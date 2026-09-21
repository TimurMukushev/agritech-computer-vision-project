from django.db import models

class TreatmentRecommendation(models.Model):
    class_name = models.CharField(max_length=100, unique=True)
    disease_display_name = models.CharField(max_length=200)
    description = models.TextField()
    treatment = models.TextField()
    treatment_duration = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.disease_display_name