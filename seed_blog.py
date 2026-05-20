import os
import django
import sys

# Configure Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'everyday_gobez.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error configuring Django: {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from blog.models import Category, Post, Comment, Profile

def seed_database():
    print("--- Starting Everyday Gobez Database Seeding ---")

    # 1. Clean existing records (Optional, safe execution)
    print("Cleaning database...")
    Comment.objects.all().delete()
    Post.objects.all().delete()
    Category.objects.all().delete()
    # Delete non-superusers to avoid lockouts
    User.objects.filter(is_superuser=False).delete()

    # 2. Create Authors
    print("Creating author accounts...")
    
    author1_user = User.objects.create_user(
        username="gobez_dev", 
        email="dev@everydaygobez.com", 
        password="password123"
    )
    profile1 = author1_user.profile
    profile1.display_name = "Clever Dev 💻"
    profile1.avatar_emoji = "💻"
    profile1.bio = "Senior Full Stack Engineer & open-source contributor. Dedicated to crafting elegant backend APIs, clean modular architectures, and blogging about technology solutions that scale."
    profile1.save()

    author2_user = User.objects.create_user(
        username="creative_mind", 
        email="creative@everydaygobez.com", 
        password="password123"
    )
    profile2 = author2_user.profile
    profile2.display_name = "Mindful Creative 🎨"
    profile2.avatar_emoji = "🎨"
    profile2.bio = "UI/UX Visual Architect & Typography enthusiast. I explore high-contrast layouts, glassmorphism filters, tailored color systems, and modern digital aesthetics to create immersive web spaces."
    profile2.save()

    author3_user = User.objects.create_user(
        username="growth_lion", 
        email="lion@everydaygobez.com", 
        password="password123"
    )
    profile3 = author3_user.profile
    profile3.display_name = "Growth Lion 🦁"
    profile3.avatar_emoji = "🦁"
    profile3.bio = "Execution strategist, habits designer, and leadership coach. I write about daily discipline, consistent growth hacks, self-empowerment, and fostering a high-performance culture."
    profile3.save()

    print(f"Created 3 authors (default login password: password123)")

    # 3. Create Categories
    print("Creating categories...")
    tech_cat = Category.objects.create(name="Technology", color_accent="hsl(263, 90%, 65%)")
    design_cat = Category.objects.create(name="Design", color_accent="hsl(325, 90%, 60%)")
    growth_cat = Category.objects.create(name="Mindset & Growth", color_accent="hsl(142, 70%, 50%)")
    lead_cat = Category.objects.create(name="Leadership", color_accent="hsl(180, 100%, 50%)")
    free_speech_cat = Category.objects.create(name="Free Speech", color_accent="hsl(0, 0%, 0%)")

    # 4. Create Detailed Blog Posts
    print("Creating articles...")
    
    # Post 1 (Tech)
    post1 = Post.objects.create(
        author=author1_user,
        category=tech_cat,
        title="Mastering Clean Architectures in Web Applications",
        content="""In the fast-paced world of web development, it is highly tempting to write rapid, ad-hoc solutions to meet demanding deadlines. However, as an application grows in complexity, technical debt accumulates, making new feature additions tedious and buggy. This is where Clean Architecture becomes critical.

Clean Architecture divides software into concentric rings, prioritizing the isolation of core business rules from external frameworks, databases, and user interfaces. 

At the center are Entities—the foundational business elements. Surrounding them are Use Cases, which represent specific workflows. The outer rings host Interface Adapters and Frameworks.

By maintaining strict boundaries, your core business logic remains fully testable and independent of the database system or styling framework. If you decide to migrate from SQL to NoSQL, or switch your frontend from a library to pure vanilla JS, only the outermost adapters require modifications.

To implement clean boundaries in your next project:
1. Identify your core domain data structures and isolate them in simple, database-agnostic models.
2. Structure your app logic so that views or controllers only interact with decoupled service layers.
3. Keep database operations encapsulated within repository interfaces.

Being Gobez in coding means writing systems that are clean, easy to read, and robust against the test of time!""",
        is_published=True,
        views_count=145
    )

    # Post 2 (Design)
    post2 = Post.objects.create(
        author=author2_user,
        category=design_cat,
        title="The Secrets of Pure Glassmorphism Design Systems",
        content="""Modern digital interfaces are evolving past standard, flat design tokens. Flat cards can often feel rigid and generic. Glassmorphism introduces depth, visual texture, and a premium tactile layer that instantly captivates the reader.

At its core, Glassmorphism mimics transparent sheets of frosted glass layered over vibrant, glowing abstract backgrounds. To achieve an impeccable glassmorphism finish, you need a precise combination of three critical styling values:

1. Backdrop Blur: The blur must be high enough to make overlay text legible while letting underlying color shapes melt together. In CSS, `backdrop-filter: blur(16px)` provides a balanced depth of field.

2. Border Highlight: A thin, high-contrast, semi-transparent border (such as `border: 1px solid rgba(255, 255, 255, 0.08)`) acts as the sharp, glistening edge of the physical glass plate, giving it clean structural definition.

3. Shadow & Background Contrast: The card background must remain subtle (`rgba(10, 15, 30, 0.55)`) combined with a dark, spacious drop shadow to visually lift the card off the screen and give it physical presence.

When designing your layout, make sure to add dynamic, smooth transitions on interactive hover states! Applying a glowing border, changing HSL highlights, or scaling up the card by 2% on hover will instantly breathe life into your user interfaces.""",
        is_published=True,
        views_count=210
    )

    # Post 3 (Growth)
    post3 = Post.objects.create(
        author=author3_user,
        category=growth_cat,
        title="Being Gobez: The Power of Daily Execution Consistency",
        content="""The Amharic word 'Gobez' (ጎበዝ) stands for cleverness, capability, courage, and daily smart action. But how do you cultivate a 'Gobez' mindset in your professional and personal life?

It is a common misconception that high achievers are driven by immense, endless motivation. In reality, motivation is highly unstable and fleeting. True success is built on the silent, uncompromising framework of daily execution consistency.

Consistency is the ultimate force multiplier. A developer who codes for one hour every single day will comfortably outclass a coder who crams eight hours once a week. The regular repetition of small, focused habits builds massive compound momentum.

To integrate consistency into your lifestyle:
1. Define your daily minimum threshold: What is the absolute smallest action you can perform towards your goal even on your worst day? Write one line of code, sketch one interface layout, or read one page of a technical book.
2. Establish strict triggers: Link your new habits to existing parts of your routine. For example, 'As soon as my morning coffee finishes brewing, I will open my editor and write.'
3. Log your consistency: Create a simple check board or use trackers to visualize your streak. Seeing your visual progress makes it psychologically difficult to break the chain.

Stop waiting for inspiration. Set up your systems, show up every single day, and watch your skills compound. Stay consistent, stay Gobez!""",
        is_published=True,
        views_count=320
    )

    # Post 4 (Leadership)
    post4 = Post.objects.create(
        author=author3_user,
        category=lead_cat,
        title="Why Great Leaders Foster Autonomous Engineering Culture",
        content="""Micro-management is the silent killer of engineering creativity. When technical leaders attempt to direct every single line of code, dictate every design pattern, and closely monitor every minute of developer activity, they inadvertently destroy trust and initiative.

High-performance engineering requires trust, clear alignment, and high autonomy. Great leaders focus on defining 'Why' a feature matters and 'What' success looks like, while delegating the 'How' entirely to the talented execution team.

Autonomy empowers developers to experiment, take calculated ownership of their features, and innovate under a supportive system. When a developer possesses absolute ownership of a system component, their pride in craft rises, resulting in cleaner code, comprehensive test suites, and robust products.

To transition your team towards autonomous operations:
1. Provide psychological safety: Allow team members to share ambitious ideas, test creative paths, and fail safely without fear of punitive measures.
2. Deliver clear business context: Explain the direct user value and business metrics of a task so developers understand how their clever engineering supports the company's growth.
3. Conduct healthy post-mortems: When systems fail, analyze the procedural gaps rather than blaming individuals. Shift the team's focus towards long-term architectural stability.

Leading clever minds means giving them the space to do clever work. Build trust, cultivate capability, and lead with empathy!""",
        is_published=True,
        views_count=180
    )

    print(f"Created 4 premium articles with detailed content.")

    # 5. Create Comments
    print("Creating comments...")
    
    # Comments for Post 1
    Comment.objects.create(
        post=post1,
        author=author2_user,
        content="This is an exceptional breakdown of clean architecture! The decoupling of the domain models from frameworks is a absolute game-changer. Thanks for sharing!"
    )
    Comment.objects.create(
        post=post1,
        author_name_anonymous="Tarik M.",
        content="Absolutely agree. I migrated a Django project from SQLite to Postgres last month, and because I kept the business logic decoupled in a service layer, it took less than an hour! Spot on article."
    )

    # Comments for Post 2
    Comment.objects.create(
        post=post2,
        author=author1_user,
        content="The styling tips here are golden. That border highlight detail makes a massive difference! I just updated my dashboard using your HSL palette and it looks stellar."
    )
    Comment.objects.create(
        post=post2,
        author_name_anonymous="Elena K.",
        content="Stunning visual breakdown! Glassmorphism when done wrong can look so messy, but these contrast and blur guidelines are perfect."
    )

    # Comments for Post 3
    Comment.objects.create(
        post=post3,
        author=author1_user,
        content="I needed this reminder today! Consistency over intensity is a philosophy I try to live by. Writing 1 lines of code every day is definitely better than occasional crams."
    )
    Comment.objects.create(
        post=post3,
        author=author2_user,
        content="ጎበዝ (Gobez) represents the exact mindset we need. Fostering daily habits rather than waiting for creative inspiration has completely transformed my design workflow."
    )
    Comment.objects.create(
        post=post3,
        author_name_anonymous="Abebe H.",
        content="Beautiful writing. This concept of the 'daily minimum threshold' is so practical. Taking tiny daily actions really works!"
    )

    print("--- Database Seeding Completed Successfully! ---")

if __name__ == "__main__":
    seed_database()
