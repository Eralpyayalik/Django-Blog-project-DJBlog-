from django.contrib import admin

from .models import Article,Comment,Category
# Register your models here.

admin.site.register(Comment)
admin.site.register(Category)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display=["title","author","created_date"]
    list_display_links=["title","author"]
    search_fields=["title"]
    list_filter=["created_date"]

    class Meta:
        model=Article

