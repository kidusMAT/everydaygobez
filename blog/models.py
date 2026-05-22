from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.html import strip_tags
import math

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500, default="A passionate writer on Everyday Gobez!")
    avatar_emoji = models.CharField(max_length=10, default="🚀")
    display_name = models.CharField(max_length=50, blank=True)
    custom_hero_html = models.TextField(blank=True, null=True, help_text="Custom HTML for the profile hero section.")
    custom_hero_css = models.TextField(blank=True, null=True, help_text="Custom CSS for the author's profile hero section.")

    def __str__(self):
        return self.display_name or self.user.username

    @property
    def name(self):
        return self.display_name or self.user.username

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color_accent = models.CharField(max_length=30, default="hsl(263, 90%, 50%)")  # For badge styles

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=400, blank=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    post_image = models.FileField(upload_to='blog/images/', blank=True, null=True)
    post_video = models.FileField(upload_to='blog/videos/', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    reading_time_minutes = models.PositiveIntegerField(default=1, blank=True)

    def save(self, *args, **kwargs):
        # Auto-slugify title
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Calculate reading time based on 200 words per minute
        word_count = len(self.content.split())
        self.reading_time_minutes = max(1, math.ceil(word_count / 200))
        
        if not self.excerpt and self.content:
            # Generate excerpt from content
            clean_content = strip_tags(self.content).replace('&nbsp;', ' ').strip()
            self.excerpt = clean_content[:180] + "..." if len(clean_content) > 180 else clean_content

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_created']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    author_name_anonymous = models.CharField(max_length=50, blank=True, default="Anonymous Reader")
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.get_author_name()} on {self.post.title}"

    def get_author_name(self):
        if self.author:
            return self.author.profile.name if hasattr(self.author, 'profile') else self.author.username
        return self.author_name_anonymous or "Anonymous Reader"

    class Meta:
        ordering = ['date_created']

# Signals to automatically create/save Profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Inquiry from {self.name}: {self.subject}"
