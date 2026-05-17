from django.db import migrations

def clear_images(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('article', '0013_comment_likes_comment_parent'),
    ]

    operations = [
        migrations.RunPython(clear_images),
    ]

