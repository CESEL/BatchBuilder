from django.contrib import admin

# Register your models here.
from main_app.models import Build


@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('repo_id', 'head_commit')
    list_filter = ('is_merged',)
