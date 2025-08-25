import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from User.models import Category
from local_events.models import LocalEvent

class Command(BaseCommand):
    help = '서울시 문화행사 API로부터 데이터를 수집하여 DB에 저장합니다.'

    def handle(self, *args, **options):
        API_KEY = "425361695a70796f3130316242564d4f" # 서울시 공공데이터 API 키
        
        # 1. DB에서 카테고리 객체를 미리 가져옵니다.
        try:
            cat_culture = Category.objects.get(name='문화.예술')
            cat_edu = Category.objects.get(name='교육.강연')
            cat_festival = Category.objects.get(name='축제.마켓')
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR('DB에 기본 카테고리가 없습니다. User 앱의 카테고리를 먼저 생성해주세요.'))
            return

        self.stdout.write("문화행사 데이터 수집을 시작합니다...")
        start_index = 1
        total_saved_count = 0
        
        while True:
            end_index = start_index + 999
            API_URL = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/culturalEventInfo/{start_index}/{end_index}/"
            
            try:
                response = requests.get(API_URL)
                data = response.json()
                result_data = data.get('culturalEventInfo', {}).get('row', [])
                if not result_data: break

                for item in result_data:
                    # 2. API의 CODENAME에 따라 카테고리를 분류합니다.
                    codename = item.get('CODENAME', '')
                    target_category = None
                    if '교육/체험' in codename:
                        target_category = cat_edu
                    elif '축제' in codename:
                        target_category = cat_festival
                    else:
                        target_category = cat_culture
                    
                    # 3. 날짜 형식이 다를 수 있으므로 안전하게 변환
                    start_dt = parse_datetime(item.get('STRTDATE'))
                    end_dt = parse_datetime(item.get('END_DATE'))
                    if not (start_dt and end_dt): continue

                    # 4. update_or_create로 중복 없이 데이터를 저장하거나 업데이트합니다.
                    lat_str = item.get('LAT')
                    lon_str = item.get('LOT')
                    latitude = None
                    longitude = None

                    try:
                        # '~' 문자가 포함된 경우, 그 앞부분만 사용
                        if lat_str and '~' in lat_str:
                            lat_str = lat_str.split('~')[0]
                        if lat_str:
                            latitude = float(lat_str)
                        
                        if lon_str and '~' in lon_str:
                            lon_str = lon_str.split('~')[0]
                        if lon_str:
                            longitude = float(lon_str)
                    except (ValueError, TypeError):
                        # 변환 중 오류가 발생하면 None으로 처리하고 넘어감
                        self.stdout.write(self.style.WARNING(f"잘못된 좌표 데이터 발견: LAT='{lat_str}', LOT='{lon_str}'"))
                        pass
                    LocalEvent.objects.update_or_create(
                        api_id=item.get('NUM'),
                        defaults={
                            'title': item.get('TITLE'),
                            'content': f"{item.get('PROGRAM', '')}\n{item.get('ETC_DESC', '')}",
                            'category': target_category,
                            'start_date': start_dt,
                            'end_date': end_dt,
                            'location_name': item.get('GUNAME'),
                            'place': item.get('PLACE'),
                            'image_url': item.get('MAIN_IMG'),
                            'org_link': item.get('ORG_LINK'),
                            'latitude': float(item['LAT']) if item.get('LAT') else None,
                            'longitude': float(item['LOT']) if item.get('LOT') else None,
                        }
                    )
                total_saved_count += len(result_data)
                self.stdout.write(f'{start_index}~{end_index} 범위에서 처리 완료.')
                start_index += 1000
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'오류 발생: {e}'))
                break
        
        self.stdout.write(self.style.SUCCESS(f'🎉 총 {total_saved_count}개의 문화행사 데이터를 성공적으로 처리했습니다.'))
