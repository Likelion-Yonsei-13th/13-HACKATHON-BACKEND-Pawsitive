import requests
from django.core.management.base import BaseCommand
from public_data.models import CulturalFacility

class Command(BaseCommand):
    help = '서울시 문화공간 API로부터 데이터를 수집하여 DB에 저장합니다.'

    def handle(self, *args, **options):
        API_KEY = "6c464d4e7370796f34377443786669"
        CulturalFacility.objects.all().delete()
        self.stdout.write("기존 문화공간 데이터를 삭제했습니다.")
        start_index = 1
        total_saved_count = 0
        
        while True:
            end_index = start_index + 999
            API_URL = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/culturalSpaceInfo/{start_index}/{end_index}/"
            try:
                response = requests.get(API_URL)
                data = response.json()
                result_data = data.get('culturalSpaceInfo', {}).get('row', [])
                if not result_data: break
                
                for item in result_data:
                    CulturalFacility.objects.create(
                        num=item.get('NUM'), subjcode=item.get('SUBJCODE'),
                        fac_name=item.get('FAC_NAME'), address=item.get('ADDR'),
                        phone=item.get('PHNE'), fax=item.get('FAX'),
                        homepage=item.get('HOMEPAGE'), open_hour=item.get('OPENHOUR'),
                        entr_fee=item.get('ENTR_FEE'), close_day=item.get('CLOSEDAY'),
                        open_day=item.get('OPEN_DAY'), seat_cnt=item.get('SEAT_CNT'),
                        main_img=item.get('MAIN_IMG'), etc_desc=item.get('ETC_DESC'),
                        fac_desc=item.get('FAC_DESC'), entrfree=item.get('ENTRFREE'),
                        subway=item.get('SUBWAY'), busstop=item.get('BUSSTOP'),
                        airport=item.get('AIRPORT')
                    )
                count_in_page = len(result_data)
                total_saved_count += count_in_page
                self.stdout.write(f'{start_index}~{end_index} 범위에서 {count_in_page}개 저장 완료.')
                start_index += 1000
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'오류 발생: {e}'))
                break
        self.stdout.write(self.style.SUCCESS(f' 총 {total_saved_count}개의 문화공간 데이터를 성공적으로 저장했습니다.'))