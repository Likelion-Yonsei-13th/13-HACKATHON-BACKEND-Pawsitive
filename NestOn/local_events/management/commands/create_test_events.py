import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

# User 앱과 local_events 앱의 모델을 가져옵니다.
from User.models import Category, Location
from local_events.models import LocalEvent

class Command(BaseCommand):
    """
    '스포츠.레저', '사회.봉사' 카테고리에 대한 테스트용 행사 데이터를 50개 생성하는
    Django 관리자 명령어입니다.
    
    실행 방법:
    python manage.py create_test_events
    """
    help = '스포츠/레저, 사회/봉사 카테고리에 대한 테스트용 행사 데이터를 50개 생성합니다.'

    def handle(self, *args, **options):
        # Faker 인스턴스 생성 (한국어 데이터)
        fake = Faker('ko_KR')
        
        # 1. 테스트에 사용할 카테고리 객체를 가져오거나, 없으면 새로 생성합니다.
        try:
            cat_sports, _ = Category.objects.get_or_create(name='스포츠.레저')
            cat_social, _ = Category.objects.get_or_create(name='사회.봉사')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'카테고리 생성 중 오류 발생: {e}'))
            return
            
        # 2. DB에 저장된 모든 지역 정보를 가져와 리스트로 만듭니다.
        locations = list(Location.objects.all())
        if not locations:
            self.stdout.write(self.style.ERROR('DB에 지역(Location) 데이터가 없습니다. 먼저 지역 데이터를 채워주세요.'))
            return

        self.stdout.write("테스트 데이터 생성을 시작합니다...")
        
        # 3. 50개의 테스트 행사 데이터를 반복문으로 생성합니다.
        for i in range(50):
            # 랜덤으로 지역 선택
            random_location = random.choice(locations)

            # '스포츠.레저'와 '사회.봉사' 카테고리 객체 중에서만 직접 랜덤으로 선택
            random_category = random.choice([cat_sports, cat_social])

            # 랜덤 날짜 생성 (현재 시간 기준 한 달 전 ~ 한 달 후)
            start_date = fake.date_time_between(start_date='-1M', end_date='+1M', tzinfo=timezone.get_current_timezone())
            end_date = start_date + timedelta(days=random.randint(1, 7))

            try:
                LocalEvent.objects.create(
                    # api_id는 실제 데이터와 겹치지 않게 'TEST-' 접두사를 붙여 생성
                    api_id=f"TEST-{i+1}", 
                    title=f"[{random_category.name}] {fake.catch_phrase()}",
                    content=fake.text(max_nb_chars=200),
                    category=random_category,
                    start_date=start_date,
                    end_date=end_date,
                    location_name=str(random_location), 
                    place=fake.address(),
                    image_url=f"https://picsum.photos/seed/{i+1}/600/400", # 테스트용 이미지
                    org_link=fake.url(),
                    latitude=random_location.latitude,
                    longitude=random_location.longitude,
                )
            except Exception as e:
                # 중복 등의 이유로 저장 실패 시 경고 메시지를 출력하고 건너뜁니다.
                self.stdout.write(self.style.WARNING(f'데이터 생성 실패 (ID: TEST-{i+1}): {e}'))
                continue

        self.stdout.write(self.style.SUCCESS(f' 총 50개의 테스트 행사 데이터를 성공적으로 생성했습니다.'))
        