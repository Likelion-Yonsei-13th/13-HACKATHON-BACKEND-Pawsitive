from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
import json
import uuid
import openai
from .models import ChatSession, ChatMessage, BotResponse
from .config import OPENAI_API_KEY, CHATBOT_CONFIG, SYSTEM_PROMPT
from board.models import Post  # 게시판 모델 import 추가
from public_data.models import PublicAlert  # 공공데이터 모델 import 추가
from local_events.models import LocalEvent  # 지역 이벤트 모델 import 추가

def generate_session_id():
    """고유한 세션 ID를 생성합니다."""
    return str(uuid.uuid4())

def extract_region_from_question(user_message):
    """질문에서 지역명을 추출"""
    try:
        prompt = f"""
        다음 질문에서 서울시 25개 구 중 하나를 찾아주세요.
        동네명, 지명, 역명 등이 포함되어 있으면 해당 구로 매핑해주세요.
        
        예시:
        - "연희동" → "서대문구"
        - "홍대" → "마포구" 
        - "강남역" → "강남구"
        - "서초" → "서초구"
        - "종로" → "종로구"
        - "용산" → "용산구"
        
        서울시 25개 구: 강남구, 서초구, 마포구, 서대문구, 종로구, 중구, 용산구, 성동구, 광진구, 동대문구, 중랑구, 성북구, 강북구, 도봉구, 노원구, 은평구, 양천구, 강서구, 구로구, 금천구, 영등포구, 동작구, 관악구, 송파구, 강동구
        
        찾으면 구 이름만 답변하고, 없으면 'none'으로 답변해주세요.
        
        질문: {user_message}
        """
        response = call_openai_api(prompt)
        region = response.strip().lower()
        return region if region != 'none' else None
    except Exception as e:
        print(f"지역명 추출 오류: {e}")
        return None

def should_use_news_data(user_message):
    """LLM이 질문이 소식 관련인지 판단"""
    try:
        prompt = f"""
        다음 질문이 지역 소식/뉴스/이슈 관련 질문인지 판단해주세요.
        'yes' 또는 'no'로만 답변해주세요.
        
        질문: {user_message}
        """
        response = call_openai_api(prompt)
        return 'yes' in response.lower()
    except Exception as e:
        print(f"질문 유형 판단 오류: {e}")
        return False

def get_structured_data(user_message):
    """LLM 기반으로 사용자 메시지와 관련된 모든 앱의 정보를 구조화된 데이터로 가져옵니다."""
    try:
        # LLM이 지역명과 질문 유형을 판단
        region = extract_region_from_question(user_message)
        is_news_question = should_use_news_data(user_message)
        
        # 기본 구조
        structured_data = {
            "title": f"{region} 종합 정보" if region else "지역 정보",
            "content": {
                "community_news": [],
                "public_alerts": [],
                "local_events": []
            },
            "metadata": {
                "region": region,
                "question_type": "news" if is_news_question else "general",
                "timestamp": timezone.now().isoformat()
            }
        }
        
        # 지역명이 없거나 소식 관련 질문이 아니면 기본 정보만 반환
        if not region or not is_news_question:
            structured_data["content"]["general_info"] = "일반적인 지역 정보를 제공합니다."
            return structured_data
        
        # 1. 게시판 정보 (board 앱)
        related_posts = Post.objects.filter(
            is_active=True,
            title__icontains=region
        ).order_by('-created_at')[:3]
        
        related_posts_content = Post.objects.filter(
            is_active=True,
            content__icontains=region
        ).order_by('-created_at')[:3]
        
        all_posts = list(related_posts) + list(related_posts_content)
        
        # 중복 제거 및 최신순 정렬
        unique_posts = []
        seen_ids = set()
        for post in all_posts:
            if post.id not in seen_ids:
                unique_posts.append(post)
                seen_ids.add(post.id)
        
        unique_posts = sorted(unique_posts, key=lambda x: x.created_at, reverse=True)[:5]
        
        for post in unique_posts:
            structured_data["content"]["community_news"].append({
                "title": post.title,
                "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                "date": post.created_at.strftime('%Y-%m-%d'),
                "views": post.view_count
            })
        
        # 2. 공공데이터 알림 정보 (public_data 앱)
        related_alerts = PublicAlert.objects.filter(
            location_name__icontains=region
        ).order_by('-published_at')[:5]
        
        for alert in related_alerts:
            structured_data["content"]["public_alerts"].append({
                "title": alert.title,
                "content": alert.content[:200] + "..." if len(alert.content) > 200 else alert.content,
                "category": alert.get_category_display(),
                "date": alert.published_at.strftime('%Y-%m-%d %H:%M'),
                "location": alert.location_name
            })
        
        # 3. 지역 이벤트 정보 (local_events 앱)
        related_events = LocalEvent.objects.filter(
            location_name__icontains=region
        ).order_by('-recommendation_score', 'start_date')[:5]
        
        for event in related_events:
            structured_data["content"]["local_events"].append({
                "title": event.title,
                "content": event.content[:200] + "..." if len(event.content) > 200 else event.content,
                "period": f"{event.start_date} ~ {event.end_date}",
                "location": event.location_name,
                "score": event.recommendation_score
            })
        
        return structured_data
            
    except Exception as e:
        print(f"구조화된 데이터 생성 오류: {e}")
        return {
            "title": "오류 발생",
            "content": {
                "error": "데이터를 가져오는 중 오류가 발생했습니다."
            },
            "metadata": {
                "region": None,
                "question_type": "error",
                "timestamp": timezone.now().isoformat()
            }
        }

def call_openai_api(prompt, model="gpt-3.5-turbo"):
    """OpenAI API를 호출합니다."""
    try:
        # OpenAI API 키 설정
        openai.api_key = OPENAI_API_KEY
        
        if not openai.api_key or openai.api_key == "sk-your-team-api-key-here":
            return None
        
        # 구조화된 데이터 가져오기
        structured_data = get_structured_data(prompt)
        
        # JSON 형식으로 답변하도록 프롬프트 수정
        enhanced_prompt = f"""
        다음 데이터를 바탕으로 사용자 질문에 답변해주세요.
        답변은 JSON 형식으로 작성해주세요.
        
        사용자 질문: {prompt}
        
        데이터: {structured_data}
        
        답변 형식:
        {{
            "title": "답변 제목",
            "content": "답변 내용 (친근하고 정중한 톤으로 작성)"
        }}
        
        주의사항:
        - title은 간결하고 명확하게 작성
        - content는 자연스럽고 친근한 톤으로 작성
        - 데이터가 있으면 그 정보를 포함하여 답변
        - 데이터가 없으면 일반적인 지역 정보로 답변
        """
            
        # 시스템 프롬프트 사용
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": enhanced_prompt}
            ],
            max_tokens=CHATBOT_CONFIG.get('max_tokens', 800),
            temperature=CHATBOT_CONFIG.get('temperature', 0.7)
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 호출 오류: {e}")
        return None

    def get_bot_response(user_message):
    """사용자 메시지에 대한 봇 응답을 생성합니다."""
    
    # 1단계: OpenAI API 사용 (주력)
    try:
        llm_response = call_openai_api(user_message)
        if llm_response and llm_response.strip():
            return llm_response.strip()
    except Exception as e:
        print(f"OpenAI API 호출 오류: {e}")
    
    # 2단계: 기본 응답 (API 실패 시 Fallback)
    default_responses = [
        "죄송합니다. 현재 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.",
        "서버 연결에 문제가 있어요. 잠시 후 다시 질문해주세요!",
        "일시적으로 답변을 생성할 수 없습니다. 잠시 후 다시 시도해주세요.",
    ]
    
    import random
    return random.choice(default_responses)

@login_required
def chat_view(request):
    """채팅 인터페이스를 보여주는 뷰"""
    # 사용자의 활성 세션 가져오기 또는 새로 생성
    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        is_active=True,
        defaults={'session_id': generate_session_id()}
    )
    
    # 기존 메시지들 가져오기
    messages = session.messages.all()
    
    context = {
        'session': session,
        'messages': messages,
    }
    return render(request, 'chatbot/chat.html', context)

@csrf_exempt
def chat_api(request):
    """채팅 API 엔드포인트"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': '메시지가 비어있습니다.'}, status=400)
            
            # 세션 가져오기
            try:
                session = ChatSession.objects.get(session_id=session_id, is_active=True)
            except ChatSession.DoesNotExist:
                return JsonResponse({'error': '유효하지 않은 세션입니다.'}, status=400)
            
            # 사용자 메시지 저장
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=message
            )
            
            # 봇 응답 생성
            bot_response_text = get_bot_response(message)
            
            # 봇 응답 저장
            bot_message = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=bot_response_text
            )
            
            return JsonResponse({
                'success': True,
                'user_message': {
                    'id': user_message.id,
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.isoformat()
                },
                'bot_message': {
                    'id': bot_message.id,
                    'content': bot_message.content,
                    'timestamp': bot_message.timestamp.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)

@csrf_exempt
def create_session(request):
    """새로운 채팅 세션을 생성하는 API"""
    if request.method == 'POST':
        try:
            session_id = generate_session_id()
            user = request.user if request.user.is_authenticated else None
            
            session = ChatSession.objects.create(
                user=user,
                session_id=session_id
            )
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'created_at': session.created_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)

def get_messages(request, session_id):
    """특정 세션의 메시지들을 가져오는 API"""
    try:
        session = get_object_or_404(ChatSession, session_id=session_id, is_active=True)
        messages = session.messages.all()
        
        message_list = []
        for message in messages:
            message_list.append({
                'id': message.id,
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_list
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def generate_session_summary(session):
    """채팅 세션의 요약을 생성합니다."""
    try:
        # 세션의 모든 메시지 가져오기
        messages = session.messages.all()
        if not messages.exists():
            return "빈 대화"
        
        # 첫 번째 사용자 메시지로 요약 생성
        first_user_message = messages.filter(message_type='user').first()
        if first_user_message:
            user_question = first_user_message.content[:50] + "..." if len(first_user_message.content) > 50 else first_user_message.content
            return f"질문: {user_question}"
        
        return "대화 내용"
        
    except Exception as e:
        print(f"세션 요약 생성 오류: {e}")
        return "대화 내용"

def get_sessions(request):
    """사용자의 모든 채팅 세션 목록을 가져오는 API"""
    try:
        # 현재 로그인한 사용자의 활성 세션들 조회
        sessions = ChatSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-created_at')
        
        session_list = []
        for session in sessions:
            # 세션 요약 생성
            summary = generate_session_summary(session)
            message_count = session.messages.count()
            last_message = session.messages.last()
            
            session_list.append({
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'summary': summary,
                'message_count': message_count,
                'last_message_time': last_message.timestamp.isoformat() if last_message else None
            })
        
        return JsonResponse({
            'success': True,
            'sessions': session_list
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
