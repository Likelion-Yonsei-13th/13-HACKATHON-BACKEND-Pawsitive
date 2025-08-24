import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from public_data.models import PublicAlert

class Command(BaseCommand):
    help = '행정안전부 재난문자 API로부터 데이터를 수집합니다.'

    def handle(self, *args, **options):
        # API 정보 (제공해주신 스크린샷 기반)
        API_URL = "https://www.safetydata.go.kr/V2/api/DSSP-IF-00247"
        SERVICE_KEY = "8TVY52GTJ766I1SD"  # 실제 발급받은 서비스 키

        params = {
            "serviceKey": SERVICE_KEY,
            "returnType": "json",
            "pageNo": "1",
            "numOfRows": "100", # 한 번에 100개씩 최신 데이터를 가져옴
        }

        try:
            response = requests.get(API_URL, params=params, verify=False)
            response.raise_for_status() # 오류 발생 시 예외 처리
            data = response.json()

            # 실제 데이터는 response['DS_DS_NATION_EMGNCY_MSG_INQ_V2'] 에 위치할 가능성이 높습니다.
            # API 응답 구조에 따라 키를 정확히 명시해야 합니다. (실제 호출 후 확인 필요)
            alerts = data.get('DS_DS_NATION_EMGNCY_MSG_INQ_V2', [])
            
            if not alerts:
                 self.stdout.write(self.style.WARNING('API 응답에서 데이터를 찾을 수 없습니다. 응답 구조를 확인하세요.'))
                 print(data) # 전체 응답 출력
                 return

            new_alerts_count = 0
            for alert_data in alerts:
                # update_or_create: unique_id가 존재하면 업데이트, 없으면 새로 생성
                _, created = PublicAlert.objects.update_or_create(
                    unique_id=alert_data['SN'], # API의 SN
                    defaults={
                        # title이 없으므로 수신지역으로 생성
                        'title': f"[재난문자] {alert_data['RCPTN_RGN_NM']}",
                        'content': alert_data['MSG_CN'], # 메시지 내용
                        'category': 'disaster', # 이 명령어는 '자연재해' 전용
                        # 날짜 형식을 datetime 객체로 변환
                        'published_at': datetime.strptime(alert_data['CRT_DT'], '%Y-%m-%d %H:%M:%S'), # 생성일시
                        'location_name': alert_data['RCPTN_RGN_NM'], # 수신지역명
                    }
                )
                if created:
                    new_alerts_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'총 {new_alerts_count}개의 새로운 재난문자 데이터를 성공적으로 저장했습니다.'))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'API 호출 중 오류 발생: {e}'))
        except (KeyError, TypeError) as e:
            self.stdout.write(self.style.ERROR(f'데이터 파싱 중 오류 발생: {e}. API 응답 구조가 예상과 다를 수 있습니다.'))