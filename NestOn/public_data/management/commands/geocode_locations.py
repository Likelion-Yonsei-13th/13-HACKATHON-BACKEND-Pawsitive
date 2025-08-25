import time
import requests
from django.core.management.base import BaseCommand
from User.models import Location

# 사용자의 카카오 REST API 키
KAKAO_API_KEY = "b47e8b19daa813dd289164e6b9eeb2b7"

class Command(BaseCommand):
    help = 'DB에 저장된 Location의 주소 정보를 카카오 API를 이용해 좌표로 변환합니다.'

    def handle(self, *args, **options):
        locations_to_geocode = Location.objects.filter(latitude__isnull=True)
        if not locations_to_geocode.exists():
            self.stdout.write(self.style.SUCCESS('모든 지역에 이미 좌표가 할당되어 있습니다.'))
            return
        self.stdout.write(f'총 {locations_to_geocode.count()}개의 지역에 대한 좌표 변환을 시작합니다...')
        for location in locations_to_geocode:
            address = f"{location.level1_city} {location.level2_district}"
            if location.level3_borough:
                address += f" {location.level3_borough}"
            headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
            params = {"query": address}
            url = "https://dapi.kakao.com/v2/local/search/address.json"
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                if data['documents']:
                    coords = data['documents'][0]
                    location.longitude = float(coords['x'])
                    location.latitude = float(coords['y'])
                    location.save()
                    self.stdout.write(self.style.SUCCESS(f'성공: {address} -> ({location.latitude}, {location.longitude})'))
                else:
                    self.stdout.write(self.style.WARNING(f'실패: {address} 의 좌표를 찾을 수 없습니다.'))
                time.sleep(0.1)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'오류 발생: {address} ({e})'))
        self.stdout.write(self.style.SUCCESS('좌표 변환 작업이 완료되었습니다.'))