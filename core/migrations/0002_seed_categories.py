from django.db import migrations

def create_initial_categories(apps, schema_editor):
    Category = apps.get_model('core', 'Category')    
    initial_categories = [
        {'name': 'Programming', 'slug': 'programming'},
        {'name': 'Design', 'slug': 'design'},
        {'name': 'Business', 'slug': 'business'},
    ]
    
    for cat_data in initial_categories:
        Category.objects.get_or_create(name=cat_data['name'], slug=cat_data['slug'])

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'), 
    ]
    operations = [
        migrations.RunPython(create_initial_categories),
    ]