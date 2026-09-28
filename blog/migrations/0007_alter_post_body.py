from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0006_alter_post_status"),
    ]
    operations = [
        migrations.AlterField(
            model_name="post",
            name="body",
            field=models.TextField(),
        ),
    ]
