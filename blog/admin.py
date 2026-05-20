from django.contrib import admin
from .models import Profile, Category, Post, Comment, ContactMessage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'avatar_emoji']
    search_fields = ['user__username', 'display_name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color_accent']
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'date_created', 'is_published', 'views_count']
    list_filter = ['is_published', 'category', 'date_created']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'author_name_anonymous', 'date_created']
    list_filter = ['date_created']
    search_fields = ['content', 'author__username', 'author_name_anonymous']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name', 'email', 'date_sent', 'is_read']
    list_filter = ['is_read', 'date_sent']
    search_fields = ['name', 'email', 'subject', 'message']
