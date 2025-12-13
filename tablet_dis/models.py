from django.db import models

class Tablet(models.Model):
    name_en = models.CharField(max_length=200)
    name_ta = models.CharField(max_length=200, blank=True, null=True)
    
    advantages_en = models.TextField(blank=True, null=True)
    advantages_ta = models.TextField(blank=True, null=True)
    
    disadvantages_en = models.TextField(blank=True, null=True)
    disadvantages_ta = models.TextField(blank=True, null=True)
    
    dosage_timing_en = models.TextField(blank=True, null=True)
    dosage_timing_ta = models.TextField(blank=True, null=True)
    
    age_group_en = models.CharField(max_length=200, blank=True, null=True)
    age_group_ta = models.CharField(max_length=200, blank=True, null=True)
    
    storage_en = models.TextField(blank=True, null=True)
    storage_ta = models.TextField(blank=True, null=True)
    
    interactions_en = models.TextField(blank=True, null=True)
    interactions_ta = models.TextField(blank=True, null=True)
    
    # Timestamp fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_en or self.name_ta or "Unnamed Tablet"

    def get_field(self, field_base, lang="en"):
        """Return the correct field value depending on the language."""
        field_name = f"{field_base}_{lang}"
        return getattr(self, field_name, None)
