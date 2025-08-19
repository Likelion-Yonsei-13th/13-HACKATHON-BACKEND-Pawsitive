# user/migrations/0002_load_categories.py

from django.db import migrations

def load_data(apps, schema_editor):
    Category = apps.get_model('User', 'Category')
    SubCategory = apps.get_model('User', 'SubCategory')

    # 카테고리 데이터 정의
    categories_data = {
        "문화.예술": ["지역공연(연극, 뮤지컬, 콘서트)", "미술 전시회, 사진전", "전통문화 체험(서예, 다도, 민속놀이)", "영화 상영회"],
        "축제.마켓": ["지역 특산물 축제", "플리마켓, 버룩시장", "푸드트럭 페스티벌", "계절별 야외축제"],
        "스포츠.레저": ["마라톤, 사이클 대회", "지역 생활체육대회", "등산, 트레킹 모임", "e-스포츠 토너먼트"],
        "교육.강연": ["주민센터 프로그램(요가, 외국어, 요리)", "전문 강연회(재테크, 창업)", "아동, 청소년 캠프", "독서 모임, 북콘서트"],
        "사회.봉사": ["환경 정화 활동", "헌혈 행사", "재능기부 봉사", "지역 안전 순찰 모임"],
        "상권.쇼핑 이벤트": ["신제품 런칭 행사", "매장 오픈 기념 프로모션", "대형 할인전", "로컬 브랜드 팝업 스토어"],
    }

    for cat_name, sub_cat_names in categories_data.items():
        category = Category.objects.create(name=cat_name)
        for sub_name in sub_cat_names:
            SubCategory.objects.create(parent_category=category, name=sub_name)

class Migration(migrations.Migration):
    dependencies = [
        ('User', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_data),
    ]