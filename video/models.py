from django.db import models, transaction
import subprocess
import os
import mysql.connector
from django.conf import settings
from datetime import datetime
from django.core.exceptions import ValidationError
from django.forms import forms
from django.utils.translation import gettext_lazy as _
from pathlib import Path
import shutil
from project.vod_settings import VOD_DB

class VideoFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        super(VideoFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(VideoFileField, self).clean(*args, **kwargs)
        if data:
            ext = os.path.splitext(data.name)[1].lower()
            valid_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm']
            if ext not in valid_extensions:
                raise forms.ValidationError(_('Please upload a valid video file. Supported formats: MP4, MKV, AVI, MOV, WEBM'))
        return data

def validate_video_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file format. Please upload a video file (MP4, MKV, AVI, MOV, or WEBM)')

class Video(models.Model):
    RESOLUTION_CHOICES = [
        ('original', 'Keep Original Resolution'),
        ('360p', '360p (640x360)'),
        ('480p', '480p (854x480)'),
        ('720p', '720p (1280x720)'),
        ('1080p', '1080p (1920x1080)'),
    ]

    MAX_VIDEO_SIZE_MB = 2500  # Maximum video size in MB (2.5GB)
    
    caption = models.CharField(max_length=100)
    video = VideoFileField(
        upload_to='video/%y',
        validators=[validate_video_extension],
        help_text='Supported formats: MP4, MKV, AVI, MOV, WEBM',
        verbose_name='Video File'
    )
    processed_video = models.URLField(max_length=500, null=True, blank=True)  # Changed to URLField
    target_resolution = models.CharField(
        max_length=10, 
        choices=RESOLUTION_CHOICES,
        default='720p',
        help_text='Target resolution for video processing'
    )

    def clean(self):
        if self.video:
            # Check file size
            if self.video.size > self.MAX_VIDEO_SIZE_MB * 1024 * 1024:
                raise ValidationError(f'Video size cannot exceed {self.MAX_VIDEO_SIZE_MB}MB')
            
            if not os.path.exists(self.video.path):
                return  # Skip duration check if file doesn't exist yet

            # Get video duration using FFprobe
            try:
                cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    str(self.video.path)
                ]
                duration = float(subprocess.check_output(cmd, text=True, stderr=subprocess.PIPE).strip())
                
                if duration > 600:  # 10 minutes
                    raise ValidationError('Video duration cannot exceed 10 minutes')
            except (subprocess.SubprocessError, ValueError, OSError) as e:
                print(f"Warning: Could not check video duration: {e}")

    def __str__(self):
        return self.caption

    def save(self, *args, **kwargs):
        if self._state.adding:  # Only process new videos
            self.clean()  # Validate before processing
            with transaction.atomic():
                super().save(*args, **kwargs)
                
                if self.video and not self.processed_video:
                    try:
                        # Ensure the video file exists
                        if not os.path.exists(self.video.path):
                            raise ValidationError("Video file not found")

                        # Create necessary directories in web folder
                        year = datetime.now().strftime('%y')
                        media_root = Path(settings.MEDIA_ROOT)
                        web_output_dir = media_root / 'processed' / year
                        web_output_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Create a directory for the HLS segments
                        base_name = Path(self.video.name).stem
                        stream_dir = web_output_dir / f"stream_{base_name}"
                        stream_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Set up HLS playlist and segment paths
                        playlist_name = "playlist.m3u8"
                        segment_pattern = "segment_%03d.ts"
                        output_playlist = stream_dir / playlist_name
                        output_segment = stream_dir / segment_pattern
                        
                        # Get video resolution using FFprobe
                        probe_cmd = [
                            'ffprobe',
                            '-v', 'error',
                            '-select_streams', 'v:0',
                            '-show_entries', 'stream=width,height',
                            '-of', 'csv=p=0',
                            str(self.video.path)
                        ]
                        try:
                            original_resolution = subprocess.check_output(probe_cmd, text=True).strip().split(',')
                            original_width, original_height = map(int, original_resolution)
                        except Exception as e:
                            print(f"Error getting video resolution: {e}")
                            original_width, original_height = 1280, 720  # Default to 720p if can't detect
                        
                        # Get resolution settings based on target_resolution
                        resolution_settings = {
                            'original': {'size': f'{original_width}x{original_height}', 'bitrate': '4000k', 'bufsize': '8000k'},
                            '360p': {'size': '640x360', 'bitrate': '800k', 'bufsize': '1600k'},
                            '480p': {'size': '854x480', 'bitrate': '1200k', 'bufsize': '2400k'},
                            '720p': {'size': '1280x720', 'bitrate': '2500k', 'bufsize': '5000k'},
                            '1080p': {'size': '1920x1080', 'bitrate': '4000k', 'bufsize': '8000k'},
                        }
                        
                        res_setting = resolution_settings[self.target_resolution]

                        # Prepare base FFmpeg command
                        ffmpeg_cmd = ['ffmpeg', '-y', '-i', str(self.video.path)]
                        
                        # Add video codec settings
                        ffmpeg_cmd.extend([
                            '-threads', '2',
                            '-c:v', 'libx264',
                            '-preset', 'veryfast',
                            '-profile:v', 'main',
                            '-level', '3.1'
                        ])

                        # Add resolution-specific parameters if not keeping original
                        if self.target_resolution != 'original':
                            width, height = res_setting["size"].split('x')
                            ffmpeg_cmd.extend([
                                '-vf', f'scale=w={width}:h={height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black'
                            ])
                        
                        # Add quality and audio settings
                        ffmpeg_cmd.extend([
                            '-maxrate', res_setting['bitrate'],
                            '-bufsize', res_setting['bufsize'],
                            '-crf', '23',
                            '-c:a', 'aac',
                            '-b:a', '128k',
                            '-ac', '2',
                            '-ar', '44100'
                        ])
                        
                        # Add HLS settings
                        ffmpeg_cmd.extend([
                            '-hls_time', '6',
                            '-hls_list_size', '0',
                            '-hls_flags', 'independent_segments',
                            '-hls_segment_type', 'mpegts',
                            '-hls_segment_filename', str(output_segment),
                            '-f', 'hls',
                            str(output_playlist)
                        ])
                        
                        print(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
                        
                        # Run FFmpeg process with proper error handling
                        # Set up environment with necessary paths
                        env = os.environ.copy()
                        env['PATH'] = '/usr/local/bin:/usr/bin:/bin:' + env.get('PATH', '')
                        
                        process = subprocess.Popen(
                            ffmpeg_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            env=env
                        )
                        
                        try:
                            print("FFmpeg process started...")
                            stdout, stderr = process.communicate(timeout=7200)  # 2 hours timeout
                            
                            if process.returncode == 0:
                                print("FFmpeg process completed successfully")
                                # Set the processed_video URL using the media URL
                                relative_path = f'processed/{year}/stream_{base_name}/{playlist_name}'
                                self.processed_video = f"{settings.MEDIA_URL.rstrip('/')}/{relative_path}"
                                super().save(update_fields=['processed_video'])
                                
                                # Ensure web server can read the files
                                os.system(f'chmod -R 755 {stream_dir}')
                                
                                # Update VOD database
                                try:
                                    conn = mysql.connector.connect(
                                        host=VOD_DB['host'],
                                        port=VOD_DB['port'],
                                        database=VOD_DB['database'],
                                        user=VOD_DB['user'],
                                        password=VOD_DB['password']
                                    )
                                    
                                    cursor = conn.cursor()
                                    
                                    # Insert into multimedia table
                                    insert_query = """
                                        INSERT INTO multimedia 
                                        (judul, link, status, created_at, updated_at, kategori_id, views)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """
                                    
                                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    
                                    cursor.execute(insert_query, (
                                        self.caption,  # judul
                                        f"http://202.169.232.239:8047/media/{relative_path}",  # link
                                        'Aktif',  # status
                                        current_time,  # created_at
                                        current_time,  # updated_at
                                        2,  # kategori_id (default to 2 - adjust as needed)
                                        0  # views
                                    ))
                                    
                                    conn.commit()
                                    print("Successfully synced with VOD database")
                                    
                                except mysql.connector.Error as err:
                                    print(f"Error updating VOD database: {err}")
                                finally:
                                    if 'conn' in locals() and conn.is_connected():
                                        cursor.close()
                                        conn.close()
                                
                            else:
                                print(f"FFmpeg Error: Process returned {process.returncode}")
                                print(f"Error details: {stderr}")
                                if stream_dir.exists():
                                    shutil.rmtree(stream_dir)
                                raise ValidationError(f"Video processing failed: {stderr}")
                                
                        except subprocess.TimeoutExpired:
                            print("FFmpeg process timed out, killing process...")
                            process.kill()
                            if stream_dir.exists():
                                shutil.rmtree(stream_dir)
                            raise ValidationError("Video processing timed out")
                            
                    except Exception as e:
                        print(f"Error processing video: {str(e)}")
                        stream_dir = web_output_dir / f"stream_{base_name}"
                        if stream_dir.exists():
                            shutil.rmtree(stream_dir)
                        raise ValidationError(f"Video processing error: {str(e)}")
        else:
            super().save(*args, **kwargs)