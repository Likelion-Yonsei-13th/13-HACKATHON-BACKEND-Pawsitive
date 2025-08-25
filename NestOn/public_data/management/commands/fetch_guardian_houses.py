import requests
from django.core.management.base import BaseCommand
from public_data.models import GuardianHouse

class Command(BaseCommand):
    help = '서울시 여성안심지킴이집 API로부터 데이터를 수집하여 DB에 저장합니다.'

    def handle(self, *args, **options):
        API_KEY = "4255494d5170796f35354f65726368" # 서울시 공공데이터 API 키
        
        # 기존 데이터를 모두 삭제하고 새로 시작
        GuardianHouse.objects.all().delete()
        self.stdout.write("기존 여성안심지킴이집 데이터를 삭제했습니다.")

        start_index = 1
        total_saved_count = 0
        
        while True:
            end_index = start_index + 999
            API_URL = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/womanSafeAreaInfo/{start_index}/{end_index}/"
            
            try:
                response = requests.get(API_URL)
                response.raise_for_status()
                data = response.json()

                # API 응답에 데이터가 있는지 확인
                result_data = data.get('womanSafeAreaInfo', {}).get('row', [])
                if not result_data:
                    self.stdout.write(self.style.SUCCESS('더 이상 가져올 데이터가 없어 작업을 종료합니다.'))
                    break # 데이터가 없으면 루프 종료

                for item in result_data:
                    GuardianHouse.objects.create(
                        brand_name=item.get('BR_NM'),
                        store_name=item.get('NM'),
                        gu_name=item.get('GU_NM'),
                        address=item.get('ADDR'),
                    )
                
                count_in_page = len(result_data)
                total_saved_count += count_in_page
                self.stdout.write(self.style.SUCCESS(f'{start_index}~{end_index} 범위에서 {count_in_page}개의 데이터를 성공적으로 저장했습니다.'))

                start_index += 1000 # 다음 페이지로 이동

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'API 호출 중 오류 발생: {e}'))
                break
            except KeyError:
                # API 응답 구조에 'womanSafeAreaInfo'가 없는 경우 (오류 또는 마지막 페이지)
                error_msg = data.get('RESULT', {}).get('MESSAGE', '알 수 없는 오류')
                self.stdout.write(self.style.WARNING(f'API 오류 또는 데이터 없음: {error_msg}'))
                break
        
        self.stdout.write(self.style.SUCCESS(f'총 {total_saved_count}개의 여성안심지킴이집 데이터를 성공적으로 저장했습니다.'))