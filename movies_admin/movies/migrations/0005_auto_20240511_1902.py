from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_rename_created_genrefilmwork_created_at_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS content.person_film_work_person_id_film_work_id_idx;",
            reverse_sql="CREATE UNIQUE INDEX IF NOT EXISTS person_film_work_person_id_film_work_id_idx ON content.person_film_work(film_work_id, person_id, role);"
        ),
        migrations.RunSQL(
            sql="CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);",
            reverse_sql="DROP INDEX IF EXISTS film_work_person_role;"
        ),
    ]