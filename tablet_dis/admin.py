from django.contrib import admin
from .models import Tablet

@admin.register(Tablet)
class TabletAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ta', 'age_group_en', 'age_group_ta']
    search_fields = ['name_en', 'name_ta']
    list_filter = ['age_group_en']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Names', {
            'fields': ('name_en', 'name_ta')
        }),
        ('Benefits/Advantages', {
            'fields': ('advantages_en', 'advantages_ta')
        }),
        ('Side Effects/Disadvantages', {
            'fields': ('disadvantages_en', 'disadvantages_ta')
        }),
        ('Dosage Information', {
            'fields': ('dosage_timing_en', 'dosage_timing_ta')
        }),
        ('Age Group', {
            'fields': ('age_group_en', 'age_group_ta')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )