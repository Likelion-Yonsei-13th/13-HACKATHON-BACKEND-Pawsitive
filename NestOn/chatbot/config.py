import os

# Chatbot Configuration Example
# 이 파일을 config.py로 복사하고 실제 API 키를 입력하세요

# OpenAI API 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', "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")

# 챗봇 설정
CHATBOT_CONFIG = {
    'default_llm': 'openai',
    'fallback_to_keywords': True,
    'max_tokens': 500,
    'temperature': 0.7,
}

# 시스템 프롬프트
SYSTEM_PROMPT = """당신은 NestOn 플랫폼의 친근하고 도움이 되는 AI 어시스턴트입니다.

다음 규칙을 따라 답변해주세요:
1. 친근하고 정중한 톤을 유지하세요
2. 한국어로 답변하세요
3. NestOn 서비스와 관련된 질문이면 자세히 설명하세요
4. 모르는 내용은 솔직히 말하고 다른 방법을 제안하세요
5. 답변은 2-3문장으로 간결하게 작성하세요
6. 이모지를 적절히 사용하여 친근감을 표현하세요"""
