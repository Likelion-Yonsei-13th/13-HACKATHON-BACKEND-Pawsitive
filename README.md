# NestOn - 지역 정보 AI 어시스턴트

## 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone https://github.com/Likelion-Yonsei-13th/13-HACKATHON-BACKEND-Pawsitive.git
cd 13-HACKATHON-BACKEND-Pawsitive
```

### 2. 가상환경 설정
```bash
# Python 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 설정
```bash
# config.py 파일 생성
cp chatbot/config.example.py chatbot/config.py

# OpenAI API 키 설정
nano chatbot/config.py
# OPENAI_API_KEY = "your-actual-api-key-here" 입력
```

### 5. 데이터베이스 설정
```bash
python manage.py migrate
```

### 6. 서버 실행
```bash
python manage.py runserver
```