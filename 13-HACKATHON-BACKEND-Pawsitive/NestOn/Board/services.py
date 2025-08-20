import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from .models import PublicNews, Location
from User.models import Location as UserLocation
from django.db.models import Q

class PublicNewsService:
    """공공기관 API에서 뉴스를 가져오는 서비스"""
    
    def __init__(self):
        self.data_go_kr_api_key = getattr(settings, 'DATA_GO_KR_API_KEY', None)
        self.seoul_api_key = getattr(settings, 'SEOUL_API_KEY', None)
    
    def fetch_seoul_news(self, location_name=None):
        """서울시 API에서 뉴스 가져오기"""
        if not self.seoul_api_key:
            return []
        
        try:
            # 서울시 공지사항 API
            url = "http://openapi.seoul.go.kr:8088/{}/json/SeoulNews/1/100/".format(self.seoul_api_key)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            news_list = []
            
            if 'SeoulNews' in data and 'row' in data['SeoulNews']:
                for item in data['SeoulNews']['row']:
                    # 지역 필터링
                    if location_name and location_name not in item.get('TITLE', ''):
                        continue
                    
                    # Location 객체 찾기
                    location = self._find_location_by_name(location_name or '서울특별시')
                    
                    if location:
                        news_data = {
                            'title': item.get('TITLE', ''),
                            'content': item.get('CONTENT', ''),
                            'summary': item.get('CONTENT', '')[:200] + '...' if len(item.get('CONTENT', '')) > 200 else item.get('CONTENT', ''),
                            'location': location,
                            'source': 'seoul',
                            'source_name': '서울시',
                            'original_url': item.get('LINK', ''),
                            'external_id': item.get('ID', ''),
                            'category': self._categorize_news(item.get('TITLE', '')),
                            'published_at': datetime.now(),  # API에서 제공하지 않는 경우
                            'is_important': '중요' in item.get('TITLE', '') or '긴급' in item.get('TITLE', '')
                        }
                        
                        news_list.append(news_data)
            
            return news_list
            
        except Exception as e:
            print(f"서울시 API 오류: {e}")
            return []
    
    def fetch_district_news(self, district_name):
        """구청 API에서 뉴스 가져오기"""
        try:
            # 구청별 API 엔드포인트 (예시)
            district_apis = {
                '서대문구': {
                    'url': 'https://api.seodaemun.go.kr/news',
                    'api_key': getattr(settings, 'SEODAEMUN_API_KEY', None)
                },
                '강남구': {
                    'url': 'https://api.gangnam.go.kr/news',
                    'api_key': getattr(settings, 'GANGNAM_API_KEY', None)
                },
                # 다른 구청들 추가
            }
            
            if district_name not in district_apis:
                return []
            
            api_config = district_apis[district_name]
            if not api_config['api_key']:
                return []
            
            headers = {
                'Authorization': f'Bearer {api_config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(api_config['url'], headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            news_list = []
            
            # 구청별 응답 형식에 따라 파싱
            for item in data.get('items', []):
                location = self._find_location_by_name(district_name)
                
                if location:
                    news_data = {
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'summary': item.get('summary', ''),
                        'location': location,
                        'source': 'district',
                        'source_name': f'{district_name}청',
                        'original_url': item.get('url', ''),
                        'external_id': item.get('id', ''),
                        'category': self._categorize_news(item.get('title', '')),
                        'published_at': datetime.fromisoformat(item.get('published_at', datetime.now().isoformat())),
                        'is_important': item.get('is_important', False)
                    }
                    
                    news_list.append(news_data)
            
            return news_list
            
        except Exception as e:
            print(f"{district_name} API 오류: {e}")
            return []
    
    def fetch_data_go_kr_news(self, location_name=None):
        """공공데이터포털 API에서 뉴스 가져오기"""
        if not self.data_go_kr_api_key:
            return []
        
        try:
            # 공공데이터포털 지역뉴스 API
            url = "http://api.data.go.kr/openapi/regional-news-api"
            params = {
                'serviceKey': self.data_go_kr_api_key,
                'pageNo': 1,
                'numOfRows': 100,
                'type': 'json'
            }
            
            if location_name:
                params['region'] = location_name
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            news_list = []
            
            # API 응답 형식에 따라 파싱
            for item in data.get('items', []):
                location = self._find_location_by_name(location_name or item.get('region', ''))
                
                if location:
                    news_data = {
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'summary': item.get('summary', ''),
                        'location': location,
                        'source': 'data_go_kr',
                        'source_name': '공공데이터포털',
                        'original_url': item.get('url', ''),
                        'external_id': item.get('id', ''),
                        'category': self._categorize_news(item.get('title', '')),
                        'published_at': datetime.fromisoformat(item.get('published_at', datetime.now().isoformat())),
                        'is_important': False
                    }
                    
                    news_list.append(news_data)
            
            return news_list
            
        except Exception as e:
            print(f"공공데이터포털 API 오류: {e}")
            return []
    
    def _find_location_by_name(self, location_name):
        """지역명으로 Location 객체 찾기"""
        try:
            # 정확한 매칭 시도
            location = UserLocation.objects.filter(
                level1_city__icontains=location_name
            ).first()
            
            if not location:
                # 부분 매칭 시도
                location = UserLocation.objects.filter(
                    level2_district__icontains=location_name
                ).first()
            
            return location
        except:
            return None
    
    def _categorize_news(self, title):
        """뉴스 제목을 보고 카테고리 분류"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['공지', '안내', '알림']):
            return 'notice'
        elif any(word in title_lower for word in ['행사', '축제', '이벤트']):
            return 'event'
        elif any(word in title_lower for word in ['문화', '예술', '전시']):
            return 'culture'
        elif any(word in title_lower for word in ['체육', '운동', '스포츠']):
            return 'sports'
        elif any(word in title_lower for word in ['교육', '학교', '학습']):
            return 'education'
        elif any(word in title_lower for word in ['복지', '보호', '지원']):
            return 'welfare'
        elif any(word in title_lower for word in ['교통', '도로', '버스', '지하철']):
            return 'transport'
        elif any(word in title_lower for word in ['환경', '공원', '녹지']):
            return 'environment'
        else:
            return 'news'
    
    def save_news_to_database(self, news_list):
        """뉴스 리스트를 데이터베이스에 저장"""
        saved_count = 0
        
        for news_data in news_list:
            try:
                # 중복 체크
                existing_news = PublicNews.objects.filter(
                    source=news_data['source'],
                    external_id=news_data['external_id']
                ).first()
                
                if not existing_news:
                    PublicNews.objects.create(**news_data)
                    saved_count += 1
                    
            except Exception as e:
                print(f"뉴스 저장 오류: {e}")
                continue
        
        return saved_count
    
    def update_all_news(self):
        """모든 소스에서 뉴스 업데이트"""
        total_saved = 0
        
        # 서울시 뉴스
        seoul_news = self.fetch_seoul_news()
        total_saved += self.save_news_to_database(seoul_news)
        
        # 구청별 뉴스
        districts = ['서대문구', '강남구', '마포구', '종로구']  # 필요한 구청들
        for district in districts:
            district_news = self.fetch_district_news(district)
            total_saved += self.save_news_to_database(district_news)
        
        # 공공데이터포털 뉴스
        data_go_news = self.fetch_data_go_kr_news()
        total_saved += self.save_news_to_database(data_go_news)
        
        return total_saved

class LocalEventService:
    """지역행사 API 서비스"""
    
    def __init__(self):
        self.seoul_api_key = getattr(settings, 'SEOUL_API_KEY', '')
        self.data_go_kr_api_key = getattr(settings, 'DATA_GO_KR_API_KEY', '')
    
    def fetch_seoul_events(self, location_name=None):
        """서울시 행사 정보 가져오기"""
        try:
            # 서울시 공공데이터 포털 API
            url = "http://openapi.seoul.go.kr:8088"
            params = {
                'key': self.seoul_api_key,
                'type': 'json',
                'service': 'SearchConcertDetailService',
                'start_index': 1,
                'end_index': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            events = []
            if 'SearchConcertDetailService' in data:
                concert_data = data['SearchConcertDetailService']['row']
                for item in concert_data:
                    event = self._parse_seoul_event(item)
                    if event:
                        events.append(event)
            
            return events
            
        except Exception as e:
            print(f"서울시 행사 API 오류: {e}")
            return []
    
    def fetch_district_events(self, district_name):
        """구청별 행사 정보 가져오기"""
        try:
            # 각 구청별 API 엔드포인트 (예시)
            district_apis = {
                '서대문구': 'https://api.seodaemun.go.kr/events',
                '강남구': 'https://api.gangnam.go.kr/events',
                '마포구': 'https://api.mapo.go.kr/events',
                # 다른 구청들 추가
            }
            
            if district_name in district_apis:
                url = district_apis[district_name]
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                events = []
                for item in data.get('events', []):
                    event = self._parse_district_event(item, district_name)
                    if event:
                        events.append(event)
                
                return events
            
            return []
            
        except Exception as e:
            print(f"{district_name} 구청 행사 API 오류: {e}")
            return []
    
    def fetch_data_go_kr_events(self):
        """공공데이터 포털 행사 정보 가져오기"""
        try:
            # 공공데이터 포털 문화행사 API
            url = "http://api.data.go.kr/openapi/cultural-event-info"
            params = {
                'serviceKey': self.data_go_kr_api_key,
                'type': 'json',
                'pageNo': 1,
                'numOfRows': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            events = []
            if 'response' in data and 'body' in data['response']:
                items = data['response']['body']['items']
                for item in items:
                    event = self._parse_data_go_kr_event(item)
                    if event:
                        events.append(event)
            
            return events
            
        except Exception as e:
            print(f"공공데이터 포털 행사 API 오류: {e}")
            return []
    
    def _parse_seoul_event(self, item):
        """서울시 행사 데이터 파싱"""
        try:
            from datetime import datetime
            from django.utils import timezone
            
            # 날짜 파싱
            start_date_str = item.get('startDate', '')
            end_date_str = item.get('endDate', '')
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
            except:
                start_date = timezone.now()
                end_date = timezone.now() + timedelta(days=1)
            
            event_data = {
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'event_start_date': start_date,
                'event_end_date': end_date,
                'event_location': item.get('place', ''),
                'event_address': item.get('address', ''),
                'event_fee': item.get('fee', '무료'),
                'event_contact': item.get('contact', ''),
                'event_website': item.get('url', ''),
                'event_image': item.get('image', ''),
                'source': '서울시',
                'source_id': item.get('id', ''),
                'api_data': item
            }
            
            return event_data
            
        except Exception as e:
            print(f"서울시 행사 데이터 파싱 오류: {e}")
            return None
    
    def _parse_district_event(self, item, district_name):
        """구청 행사 데이터 파싱"""
        try:
            from datetime import datetime
            from django.utils import timezone
            
            # 날짜 파싱
            start_date_str = item.get('start_date', '')
            end_date_str = item.get('end_date', '')
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
            except:
                start_date = timezone.now()
                end_date = timezone.now() + timedelta(days=1)
            
            event_data = {
                'title': item.get('title', ''),
                'content': item.get('description', ''),
                'event_start_date': start_date,
                'event_end_date': end_date,
                'event_location': item.get('venue', ''),
                'event_address': item.get('address', ''),
                'event_fee': item.get('fee', '무료'),
                'event_contact': item.get('contact', ''),
                'event_website': item.get('website', ''),
                'event_image': item.get('image', ''),
                'source': f'{district_name}구청',
                'source_id': item.get('id', ''),
                'api_data': item
            }
            
            return event_data
            
        except Exception as e:
            print(f"{district_name} 구청 행사 데이터 파싱 오류: {e}")
            return None
    
    def _parse_data_go_kr_event(self, item):
        """공공데이터 포털 행사 데이터 파싱"""
        try:
            from datetime import datetime
            from django.utils import timezone
            
            # 날짜 파싱
            start_date_str = item.get('startDate', '')
            end_date_str = item.get('endDate', '')
            
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except:
                start_date = timezone.now()
                end_date = timezone.now() + timedelta(days=1)
            
            event_data = {
                'title': item.get('title', ''),
                'content': item.get('description', ''),
                'event_start_date': start_date,
                'event_end_date': end_date,
                'event_location': item.get('venue', ''),
                'event_address': item.get('address', ''),
                'event_fee': item.get('fee', '무료'),
                'event_contact': item.get('contact', ''),
                'event_website': item.get('url', ''),
                'event_image': item.get('image', ''),
                'source': '공공데이터 포털',
                'source_id': item.get('id', ''),
                'api_data': item
            }
            
            return event_data
            
        except Exception as e:
            print(f"공공데이터 포털 행사 데이터 파싱 오류: {e}")
            return None
    
    def _find_location_by_name(self, location_name):
        """지역명으로 Location 객체 찾기"""
        try:
            from User.models import Location
            return Location.objects.filter(
                Q(level2_district__icontains=location_name) |
                Q(level3_borough__icontains=location_name)
            ).first()
        except:
            return None
    
    def _categorize_event(self, title, content):
        """행사 제목과 내용으로 카테고리 분류"""
        try:
            from User.models import Category, SubCategory
            
            text = f"{title} {content}".lower()
            
            # 카테고리 매핑
            category_mapping = {
                '문화': ['문화', '공연', '전시', '축제', '음악', '댄스', '연극'],
                '교육': ['교육', '강연', '워크샵', '세미나', '강좌', '학습'],
                '체육': ['체육', '운동', '스포츠', '마라톤', '축구', '야구'],
                '복지': ['복지', '건강', '의료', '상담', '지원'],
                '환경': ['환경', '청소', '재활용', '녹지', '공원'],
                '교통': ['교통', '도로', '버스', '지하철', '주차'],
                '행정': ['행정', '민원', '서류', '신청', '접수']
            }
            
            for category_name, keywords in category_mapping.items():
                if any(keyword in text for keyword in keywords):
                    category = Category.objects.filter(name=category_name).first()
                    return category
            
            # 기본값
            return Category.objects.first()
            
        except:
            return Category.objects.first()
    
    def save_event_to_database(self, event_data):
        """행사 데이터를 데이터베이스에 저장"""
        try:
            from .models import LocalEvent
            from User.models import Location, Category
            
            # 중복 체크
            existing_event = LocalEvent.objects.filter(
                source_id=event_data['source_id'],
                source=event_data['source']
            ).first()
            
            if existing_event:
                # 기존 데이터 업데이트
                for key, value in event_data.items():
                    if hasattr(existing_event, key):
                        setattr(existing_event, key, value)
                existing_event.save()
                return existing_event
            
            # 새 행사 생성
            location = self._find_location_by_name(event_data.get('location_name', ''))
            category = self._categorize_event(event_data['title'], event_data['content'])
            
            event = LocalEvent.objects.create(
                title=event_data['title'],
                content=event_data['content'],
                location=location or Location.objects.first(),
                category=category,
                event_start_date=event_data['event_start_date'],
                event_end_date=event_data['event_end_date'],
                event_location=event_data['event_location'],
                event_address=event_data['event_address'],
                event_fee=event_data['event_fee'],
                event_contact=event_data['event_contact'],
                event_website=event_data['event_website'],
                event_image=event_data['event_image'],
                source=event_data['source'],
                source_id=event_data['source_id'],
                api_data=event_data['api_data'],
                is_free=event_data['event_fee'] == '무료'
            )
            
            return event
            
        except Exception as e:
            print(f"행사 데이터 저장 오류: {e}")
            return None
    
    def update_all_events(self):
        """모든 행사 데이터 업데이트"""
        try:
            # 서울시 행사 가져오기
            seoul_events = self.fetch_seoul_events()
            for event_data in seoul_events:
                self.save_event_to_database(event_data)
            
            # 구청별 행사 가져오기
            districts = ['서대문구', '강남구', '마포구', '종로구', '중구']
            for district in districts:
                district_events = self.fetch_district_events(district)
                for event_data in district_events:
                    event_data['location_name'] = district
                    self.save_event_to_database(event_data)
            
            # 공공데이터 포털 행사 가져오기
            data_go_events = self.fetch_data_go_kr_events()
            for event_data in data_go_events:
                self.save_event_to_database(event_data)
            
            return True
            
        except Exception as e:
            print(f"행사 데이터 업데이트 오류: {e}")
            return False
