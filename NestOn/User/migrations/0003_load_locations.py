# User/migrations/0002_load_locations.py

import csv
from django.db import migrations
from django.conf import settings

# 1단계에서 저장한 CSV 파일 경로
CSV_PATH = settings.BASE_DIR / 'data' / 'korea_locations_3level.csv'

def load_data(apps, schema_editor):
    Location = apps.get_model('User', 'Location') # 'user' -> 'User'로 수정
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        data_reader = csv.DictReader(csvfile)
        locations_to_create = []
        for row in data_reader:
            # CSV의 level3_borough가 비어있는 경우 None으로 처리
            level3_borough = row['level3_borough'] if row['level3_borough'] else None

            locations_to_create.append(
                Location(
                    level1_city=row['level1_city'],
                    level2_district=row['level2_district'],
                    level3_borough=level3_borough
                )
            )

        # bulk_create로 모든 데이터를 한 번에 효율적으로 삽입
        Location.objects.bulk_create(locations_to_create)

class Migration(migrations.Migration):
    dependencies = [
        ('User', '0001_initial'), # 'user' -> 'User'로 수정
    ]
    operations = [
        migrations.RunPython(load_data), # load_data 함수 실행
    ]