from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Post, Comment, Profile, ContactMessage
from django.utils.text import slugify
import requests
import secrets
import random
from django.urls import reverse
from django.conf import settings


def auth_login(request):
    if request.user.is_authenticated:
        return redirect('post_list')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Check if the user tried logging in with email
        user = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                username = username_or_email
        else:
            username = username_or_email

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.profile.name}! Ready to be Gobez today?")
            return redirect('post_list')
        else:
            messages.error(request, "Invalid username/email or password. Please try again.")
            
    return render(request, 'blog/auth/login.html')

def google_login(request):
    if request.user.is_authenticated:
        return redirect('post_list')
        
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    
    redirect_uri = request.build_absolute_uri(reverse('google_callback'))
    
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=openid%20email%20profile"
        f"&state={state}"
        f"&prompt=select_account"
    )
    return redirect(auth_url)

def google_callback(request):
    if request.user.is_authenticated:
        return redirect('post_list')
        
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f"Google authentication failed: {error}")
        return redirect('login')
        
    session_state = request.session.pop('google_oauth_state', None)
    if not state or state != session_state:
        messages.error(request, "Invalid authentication state. Please try again.")
        return redirect('login')
        
    if not code:
        messages.error(request, "Authorization code not provided by Google.")
        return redirect('login')
        
    redirect_uri = request.build_absolute_uri(reverse('google_callback'))
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json.get('access_token')
    except Exception as e:
        messages.error(request, f"Failed to retrieve access token from Google: {str(e)}")
        return redirect('login')
        
    if not access_token:
        messages.error(request, "Failed to retrieve access token from Google response.")
        return redirect('login')
        
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
    except Exception as e:
        messages.error(request, f"Failed to retrieve profile info from Google: {str(e)}")
        return redirect('login')
        
    email = userinfo.get('email')
    name = userinfo.get('name') or userinfo.get('given_name') or "Google User"
    
    if not email:
        messages.error(request, "Google login failed: Email address not provided.")
        return redirect('login')
        
    user = User.objects.filter(email=email).first()
    
    if user:
        login(request, user)
        messages.success(request, f"Welcome back, {user.profile.name}! Logged in with Google.")
    else:
        email_username = email.split('@')[0].strip().lower()
        username = ''.join(c for c in email_username if c.isalnum() or c in ['_', '-'])
        if not username:
            username = "user"
            
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        try:
            password = secrets.token_urlsafe(16)
            user = User.objects.create_user(username=username, email=email, password=password)
            
            profile = user.profile
            profile.display_name = name
            
            emojis = ['🚀', '🧠', '💻', '🎨', '🦁', '⚡', '✨', '🔥', '📚', '🌟', '🦄', '🎯']
            profile.avatar_emoji = random.choice(emojis)
            profile.bio = "Logged in using Google on Everyday Gobez!"
            profile.save()
            
            login(request, user)
            messages.success(request, f"Welcome to Everyday Gobez, {profile.name}! Account created with Google.")
        except Exception as e:
            messages.error(request, f"Failed to create account: {str(e)}")
            return redirect('login')
            
    return redirect('post_list')

def auth_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully. Stay Gobez, come back soon!")
    return redirect('post_list')

def auth_register(request):
    if request.user.is_authenticated:
        return redirect('post_list')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        display_name = request.POST.get('display_name', '').strip()
        avatar_emoji = request.POST.get('avatar_emoji', '🚀')
        bio = request.POST.get('bio', '').strip()

        # Validations
        if not username or not email or not password:
            messages.error(request, "All core fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
        else:
            # Create user and profile
            user = User.objects.create_user(username=username, email=email, password=password)
            profile = user.profile
            profile.display_name = display_name or username.capitalize()
            profile.avatar_emoji = avatar_emoji
            profile.bio = bio or "A newly registered writer on Everyday Gobez!"
            profile.save()
            
            # Log the user in
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {profile.name}!")
            return redirect('post_list')

    # Available avatars list for interactive select option
    emojis = ['🚀', '🧠', '💻', '🎨', '🦁', '⚡', '✨', '🔥', '📚', '🌟', '🦄', '🎯']
    return render(request, 'blog/auth/register.html', {'emojis': emojis})

@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        display_name = request.POST.get('display_name', '').strip()
        avatar_emoji = request.POST.get('avatar_emoji', '🚀')
        bio = request.POST.get('bio', '').strip()

        profile.display_name = display_name
        profile.avatar_emoji = avatar_emoji
        profile.bio = bio
        profile.save()
        messages.success(request, "Your profile was updated successfully!")
        return redirect('post_list')

    emojis = ['🚀', '🧠', '💻', '🎨', '🦁', '⚡', '✨', '🔥', '📚', '🌟', '🦄', '🎯']
    return render(request, 'blog/auth/profile_edit.html', {'profile': profile, 'emojis': emojis})

def post_list(request, category_slug=None):
    posts = Post.objects.filter(is_published=True)
    categories = Category.objects.all()
    selected_category = None
    search_query = request.GET.get('search', '').strip()

    # Category filter
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=selected_category)

    # Search query filter
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__profile__display_name__icontains=search_query)
        )

    # Featured post (highest views or most recent)
    featured_post = posts.first() if posts.exists() else None
    recent_posts = posts[1:] if posts.exists() else []

    context = {
        'posts': posts,
        'recent_posts': recent_posts,
        'featured_post': featured_post,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    return render(request, 'blog/post_list.html', context)

def author_feed(request, username):
    author_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author_user, is_published=True)
    categories = Category.objects.all()

    context = {
        'author_user': author_user,
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'blog/author_feed.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Increment views count
    post.views_count += 1
    post.save(update_fields=['views_count'])

    comments = post.comments.all()
    categories = Category.objects.all()
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'categories': categories
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        category_id = request.POST.get('category')
        custom_category_name = request.POST.get('custom_category', '').strip()
        is_published = request.POST.get('is_published') == 'on' or request.POST.get('action') == 'publish'
        post_image = request.FILES.get('post_image')
        post_video = request.FILES.get('post_video')

        if not title or not content:
            messages.error(request, "Title and Content are required.")
        else:
            category = None
            if category_id == 'new_category' and custom_category_name:
                category = Category.objects.filter(name__iexact=custom_category_name).first()
                if not category:
                    category = Category.objects.create(
                        name=custom_category_name,
                        color_accent='hsl(0, 0%, 0%)'
                    )
            elif category_id and category_id.isdigit():
                category = Category.objects.filter(id=category_id).first()

            post = Post.objects.create(
                author=request.user,
                title=title,
                content=content,
                category=category,
                post_image=post_image,
                post_video=post_video,
                is_published=is_published
            )
            messages.success(request, "Blog post published successfully!" if is_published else "Draft saved successfully!")
            return redirect('post_detail', slug=post.slug)

    categories = Category.objects.all()
    return render(request, 'blog/post_form.html', {'categories': categories, 'action_type': 'Create'})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Permission verification
    if post.author != request.user:
        messages.error(request, "Permission denied. You can only edit your own posts.")
        return redirect('post_detail', slug=post.slug)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '')
        category_id = request.POST.get('category')
        custom_category_name = request.POST.get('custom_category', '').strip()
        is_published = request.POST.get('is_published') == 'on' or request.POST.get('action') == 'publish'
        post_image = request.FILES.get('post_image')
        post_video = request.FILES.get('post_video')
        clear_image = request.POST.get('clear_image') == 'on'
        clear_video = request.POST.get('clear_video') == 'on'

        if not title or not content:
            messages.error(request, "Title and Content are required.")
        else:
            category = None
            if category_id == 'new_category' and custom_category_name:
                category = Category.objects.filter(name__iexact=custom_category_name).first()
                if not category:
                    category = Category.objects.create(
                        name=custom_category_name,
                        color_accent='hsl(0, 0%, 0%)'
                    )
            elif category_id and category_id.isdigit():
                category = Category.objects.filter(id=category_id).first()

            post.title = title
            post.content = content
            post.category = category
            
            if clear_image:
                if post.post_image:
                    post.post_image.delete(save=False)
                post.post_image = None
            elif post_image:
                post.post_image = post_image

            if clear_video:
                if post.post_video:
                    post.post_video.delete(save=False)
                post.post_video = None
            elif post_video:
                post.post_video = post_video

            post.is_published = is_published
            post.save()
            messages.success(request, "Blog post updated successfully!")
            return redirect('post_detail', slug=post.slug)

    categories = Category.objects.all()
    return render(request, 'blog/post_form.html', {'post': post, 'categories': categories, 'action_type': 'Edit'})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Permission verification
    if post.author != request.user:
        messages.error(request, "Permission denied. You can only delete your own posts.")
        return redirect('post_detail', slug=post.slug)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Blog post deleted successfully.")
        return redirect('post_list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})

def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Comment content cannot be empty.'}, status=400)
            messages.error(request, "Comment content cannot be empty.")
            return redirect('post_detail', slug=post.slug)

        comment = Comment(post=post, content=content)
        if request.user.is_authenticated:
            comment.author = request.user
        else:
            comment.author_name_anonymous = request.POST.get('author_name', '').strip() or "Anonymous Reader"
        
        comment.save()

        # If AJAX, return comment details
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            return JsonResponse({
                'success': True,
                'author': comment.get_author_name(),
                'avatar': request.user.profile.avatar_emoji if request.user.is_authenticated else "👤",
                'content': comment.content,
                'date': comment.date_created.strftime("%b %d, %Y at %H:%M")
            })

        messages.success(request, "Comment posted successfully!")
        return redirect('post_detail', slug=post.slug)

    return redirect('post_detail', slug=post.slug)

def contact_us(request):
    import time
    if request.method == 'POST':
        # 1. Anti-Spam Honeypot Check
        honeypot = request.POST.get('website_url_honey', '')
        if honeypot:
            # Bot detected: fail silently by pretending it was successful
            messages.success(request, "Thank you! Your message has been sent successfully. We will reach back shortly.")
            return redirect('contact_us')
            
        # 2. Rate Limiting Check (max 1 message every 3 minutes per session)
        last_submission = request.session.get('last_contact_time', 0)
        current_time = time.time()
        if current_time - last_submission < 180: # 180 seconds = 3 minutes
            messages.error(request, "You are sending messages too quickly. Please wait a few minutes before trying again.")
            return redirect('contact_us')

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message:
            messages.error(request, "All fields are required to submit your contact request.")
        else:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            # Send email notification
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                send_mail(
                    subject=f"New Contact Request: {subject}",
                    message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@everydaygobez.com'),
                    recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'admin@everydaygobez.com')],
                    fail_silently=True,
                )
            except Exception:
                pass

            request.session['last_contact_time'] = current_time
            messages.success(request, f"Thank you, {name}! Your message has been sent successfully. We will reach back shortly.")
            return redirect('contact_us')

    return render(request, 'blog/contact.html')
