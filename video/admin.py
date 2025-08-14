from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Video

class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = '__all__'
        widgets = {
            'video': forms.FileInput(attrs={
                'accept': 'video/mp4,video/x-matroska,video/avi,video/quicktime,video/webm'
            })
        }

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    form = VideoAdminForm
    list_display = ['caption', 'video', 'target_resolution', 'processed_video_link']
    readonly_fields = ['processed_video']
    list_filter = ['target_resolution']
    actions = ['reprocess_video']
    
    def processed_video_link(self, obj):
        if obj.processed_video:
            return format_html('<a href="{}" target="_blank">{}</a>', 
                obj.processed_video, 
                obj.processed_video)
        return "-"
    processed_video_link.short_description = 'Processed Video'
    
    def reprocess_video(self, request, queryset):
        for video in queryset:
            # Clear the processed video URL to trigger reprocessing
            video.processed_video = None
            video.save()
        self.message_user(request, f"{len(queryset)} videos queued for reprocessing.")
    reprocess_video.short_description = "Reprocess selected videos"

    fieldsets = (
        (None, {
            'fields': ('caption', 'video')
        }),
        ('Processing Options', {
            'fields': ('target_resolution', 'processed_video'),
            'classes': ('collapse',),
            'description': 'Select the target resolution for video processing. Changes require reprocessing the video.'
        }),
    )