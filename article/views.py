from django.shortcuts import get_object_or_404, render,HttpResponse,redirect,reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from article.models import Article,Comment,Category
from.forms import ArticleForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum
import os
from django.contrib.auth.models import User

# Create your views here.

def articles(request):
    keyword = request.GET.get("keyword")
    category_slug = request.GET.get("category") 
    categories = Category.objects.all() 

    articles_queryset = Article.objects.annotate(like_count=Count('likes'))
    
    if keyword:
        articles = articles_queryset.filter(title__contains=keyword)
    
    elif category_slug:
        articles = articles_queryset.filter(category__slug=category_slug)
    
    else:
        articles = articles_queryset.all()

    return render(request, "articles.html", {
        "articles": articles,
        "categories": categories 
    })

"""
def articles(request):
    keyword=request.GET.get("keyword")

    if keyword:
        articles=Article.objects.filter(title__contains=keyword)
        return render(request,"articles.html",{"articles":articles})
    articles=Article.objects.all()
    return render(request,"articles.html",{"articles":articles})
"""
from django.core.paginator import Paginator

def index(request):
    articles_list = Article.objects.all().order_by('-created_date')
    
    # 6 articles per page
    paginator = Paginator(articles_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    latest_article = articles_list.first()

    popular_articles = Article.objects.all().order_by('-read_count')[:2]

    top_liked_articles = Article.objects.annotate(
        like_count=Count('likes')
    ).order_by('-like_count')[:5] 
    
    all_users = list(User.objects.all())
    top_users = sorted(all_users, key=lambda u: u.profile.total_xp, reverse=True)[:5]

    most_commented_articles = Article.objects.annotate(
        comment_count=Count('comments') 
    ).order_by('-comment_count')[:5]

    # AJAX Load More support
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        articles_data = []
        for article in page_obj:
            if article.id != latest_article.id:
                articles_data.append({
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'content': article.content[:100], # Basic strip done in JS/template or here
                    'image_url': article.article_image.url if article.article_image else None,
                    'author': article.author.username,
                    'author_image': article.author.profile.image.url if article.author.profile.image else '/static/img/default-user.png',
                    'date': article.created_date.strftime("%d %b"),
                    'category': article.category.name if article.category else 'Teknoloji'
                })
        return JsonResponse({
            'articles': articles_data,
            'has_next': page_obj.has_next(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None
        })

    return render(request, 'index.html', {
        'articles': page_obj, # Use page_obj instead of full articles list
        'latest_article': latest_article,
        'popular_articles': popular_articles,
        'top_liked_articles': top_liked_articles,
        'top_users': top_users,
        'most_commented_articles': most_commented_articles,
        'page_obj': page_obj
    })


def about(request):
    return render(request,"about.html")


@login_required(login_url="user:login")
def dashboard(request):
    articles = Article.objects.filter(author=request.user)
    
    total_articles = articles.count()
    
    total_views = articles.aggregate(Sum('read_count'))['read_count__sum'] or 0
    
    total_likes = 0
    for article in articles:
        total_likes += article.likes.count()

    context = {
        "articles": articles,
        "total_articles": total_articles,
        "total_views": total_views,
        "total_likes": total_likes,
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="user:login")
def addArticle(request):
    form=ArticleForm(request.POST or None,request.FILES or None)

    if form.is_valid():
        article=form.save(commit=False)
        article.author = request.user
        article.save()

        messages.success(request,"Makale Başarıyla Oluşturuldu.")
        return redirect("index")

    return render(request,"addarticle.html",{"form":form})
    
def detail(request, slug):
    article = get_object_or_404(Article.objects.annotate(like_count=Count('likes')), slug=slug)
 
    session_key = f'viewed_article_{article.id}' 
    
    if not request.session.get(session_key, False):
        article.read_count += 1
        article.save(update_fields=['read_count']) 

        request.session[session_key] = True 

    comments = article.comments.filter(parent=None)

    return render(request, "detail.html", {
        "article": article,
        "comments": comments
    })


@login_required(login_url="user:login")
def updateArticle(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    if article.author != request.user:
        messages.error(request, "Bu makaleyi güncellemeye yetkiniz yok!")
        return redirect("article:dashboard")

    old_image_path = article.article_image.path if article.article_image else None

    form = ArticleForm(request.POST or None, request.FILES or None, instance=article)

    if form.is_valid():
        updated_article = form.save(commit=False)
        updated_article.author = request.user
        
        if 'article_image' in request.FILES and old_image_path:
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        updated_article.save()

        messages.success(request, "Makale başarıyla güncellendi.")
        return redirect("article:dashboard") 

    return render(request, "update.html", {"form": form, "article": article})

@login_required(login_url="user:login")
def deleteArticle(request,slug):
    article=get_object_or_404(Article,slug=slug)
    article.delete()

    messages.success(request,"Makale silindi.")
    return redirect("article:dashboard")

def addComment(request, id):
    article = get_object_or_404(Article, id=id)
    if request.method == "POST":
        author = request.POST.get("comment_author")
        content = request.POST.get("comment_content")
        parent_id = request.POST.get("parent_id") 
        
        newComment = Comment(comment_author=author, comment_content=content, article=article)
        
        # EĞER BİR YANITSA ÜST YORUMA BAĞLA
        if parent_id:
            try:
                parent_obj = Comment.objects.get(id=parent_id)
                newComment.parent = parent_obj
            except Comment.DoesNotExist:
                pass
            
        if request.user.is_authenticated:
            newComment.user = request.user
        newComment.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            user_image = None
            rank_info = {"title": "MİSAFİR", "color": "#6c757d", "icon": "fa-ghost"}
            total_xp = 0

            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                if request.user.profile.image:
                    user_image = request.user.profile.image.url
                rank_info = request.user.profile.rank_info 
                total_xp = request.user.profile.total_xp

            return JsonResponse({
                'status': 'success',
                'username': author,
                'content': content,
                'user_image': user_image,
                'rank_title': rank_info.get('title'),
                'rank_color': rank_info.get('color'),
                'rank_icon': rank_info.get('icon'),
                'total_xp': total_xp,
                'is_author': (author == article.author.username),
                'is_registered_user': request.user.is_authenticated, 
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
                'parent_id': parent_id 
            })
            
    
    return redirect('article:detail', slug=article.slug)

def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    articles = category.articles.all()
    return render(request, 'category_detail.html', {'articles': articles, 'category': category})


@login_required(login_url="user:login")
def like_article(request, id):
    article = get_object_or_404(Article, id=id)
    
    if article.likes.filter(id=request.user.id).exists():
        article.likes.remove(request.user)
        liked = False
    else:
        article.likes.add(request.user)
        liked = True
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': article.likes.count()})
    
    return redirect("article:detail", id=id)
    

@login_required
def likeComment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': comment.likes.count()})
        
    return redirect('article:detail', slug=comment.article.slug)
    
