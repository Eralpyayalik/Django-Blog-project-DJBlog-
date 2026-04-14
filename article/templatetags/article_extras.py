from django import template
from django.utils.html import strip_tags
import math

register = template.Library()

@register.filter(name='read_time')
def read_time(html_content):

    if not html_content:
        return 1    
    text = strip_tags(html_content)
    
    word_count = len(text.split())
    
    minutes = math.ceil(word_count / 200)
    
    if minutes < 1:
        return 1
        
    return minutes