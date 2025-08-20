# Board 앱 API 문서

## 개요
지역 기반 게시판 기능을 제공하는 API입니다. **두 개의 게시판**으로 구성되어 있습니다:

1. **커뮤니티 게시판**: 사용자들이 직접 작성하는 게시글
2. **공공 뉴스 게시판**: 구청/시청 API에서 가져온 공식 소식

## API 엔드포인트

# ========================================
# 1. 커뮤니티 게시판 (사용자 작성)
# ========================================

### 1. 커뮤니티 게시글 목록 조회
**GET** `/api/board/community/posts/`

**쿼리 파라미터:**
- `location_id` (optional): 지역 ID로 필터링
- `category_id` (optional): 카테고리 ID로 필터링
- `subcategory_id` (optional): 서브카테고리 ID로 필터링
- `search` (optional): 제목/내용 검색
- `page` (optional): 페이지 번호 (기본값: 1)
- `page_size` (optional): 페이지당 게시글 수 (기본값: 20)

**응답 예시:**
```json
{
    "status": 200,
    "success": true,
    "message": "커뮤니티 게시글 목록 조회 성공",
    "data": {
        "posts": [
            {
                "id": 1,
                "title": "강남구 맛집 추천",
                "author_username": "user123",
                "author_name": "홍길동",
                "location_display": "서울특별시 강남구",
                "category_name": "음식",
                "subcategory_name": "맛집",
                "created_at": "2024-01-15T10:30:00Z",
                "view_count": 150,
                "comment_count": 5,
                "like_count": 12,
                "is_liked": false,
                "is_pinned": false
            }
        ],
        "total_count": 50,
        "page": 1,
        "page_size": 20
    }
}
```

### 2. 커뮤니티 게시글 상세 조회
**GET** `/api/board/community/posts/{post_id}/`

### 3. 커뮤니티 게시글 작성
**POST** `/api/board/community/posts/create/`

**요청 본문:**
```json
{
    "title": "강남구 맛집 추천",
    "content": "강남구에 있는 맛집들을 소개합니다...",
    "location_id": 1,
    "category_id": 1,
    "subcategory_id": 1
}
```

### 4. 커뮤니티 게시글 수정
**PATCH** `/api/board/community/posts/{post_id}/update/`

### 5. 커뮤니티 게시글 삭제
**DELETE** `/api/board/community/posts/{post_id}/delete/`

### 6. 커뮤니티 게시글 좋아요/취소
**POST** `/api/board/community/posts/{post_id}/like/`

### 7. 커뮤니티 댓글 작성
**POST** `/api/board/community/posts/{post_id}/comments/`

**요청 본문:**
```json
{
    "content": "정말 맛있어 보이네요!",
    "parent_id": null  // 대댓글인 경우 부모 댓글 ID
}
```

### 8. 커뮤니티 인기 게시글 조회
**GET** `/api/board/community/popular/`

**쿼리 파라미터:**
- `location_id` (optional): 지역 ID로 필터링
- `limit` (optional): 조회할 게시글 수 (기본값: 10)

# ========================================
# 2. 공공 뉴스 게시판 (구청/시청 API)
# ========================================

### 1. 공공 뉴스 목록 조회
**GET** `/api/board/news/`

**쿼리 파라미터:**
- `location_id` (optional): 지역 ID로 필터링
- `category` (optional): 카테고리로 필터링 (notice, news, event, culture, sports, education, welfare, transport, environment, other)
- `source` (optional): 출처로 필터링 (seoul, district, data_go_kr, other)
- `search` (optional): 제목/내용 검색
- `page` (optional): 페이지 번호 (기본값: 1)
- `page_size` (optional): 페이지당 뉴스 수 (기본값: 20)

**응답 예시:**
```json
{
    "status": 200,
    "success": true,
    "message": "공공 뉴스 목록 조회 성공",
    "data": {
        "news": [
            {
                "id": 1,
                "title": "서대문구 문화행사 안내",
                "summary": "서대문구에서 개최되는 문화행사에 대한 안내입니다...",
                "location_display": "서울특별시 서대문구",
                "source_name": "서대문구청",
                "category_display": "문화",
                "source_display": "구청",
                "published_at": "2024-01-15T10:30:00Z",
                "view_count": 150,
                "comment_count": 3,
                "like_count": 8,
                "is_liked": false,
                "is_important": false,
                "original_url": "https://www.seodaemun.go.kr/news/123"
            }
        ],
        "total_count": 50,
        "page": 1,
        "page_size": 20
    }
}
```

### 2. 공공 뉴스 상세 조회
**GET** `/api/board/news/{news_id}/`

### 3. 공공 뉴스 댓글 작성
**POST** `/api/board/news/{news_id}/comments/`

**요청 본문:**
```json
{
    "content": "정말 유용한 정보네요!",
    "parent_id": null  // 대댓글인 경우 부모 댓글 ID
}
```

### 4. 공공 뉴스 좋아요/취소
**POST** `/api/board/news/{news_id}/like/`

### 5. 뉴스 구독 설정
**POST** `/api/board/news/subscription/`

**요청 본문:**
```json
{
    "location_id": 1,
    "category": "culture",
    "is_active": true
}
```

### 6. 뉴스 업데이트 (관리자용)
**POST** `/api/board/news/update/`

## 인증
- 커뮤니티 게시글 작성, 수정, 삭제, 좋아요, 댓글 작성은 로그인이 필요합니다.
- 공공 뉴스 조회는 로그인 없이도 가능합니다.
- 공공 뉴스 댓글 작성, 좋아요는 로그인이 필요합니다.

## 에러 응답
모든 API는 일관된 에러 응답 형식을 사용합니다:

```json
{
    "status": 400,
    "success": false,
    "message": "에러 메시지",
    "data": null
}
```

## 사용 예시

### 커뮤니티 게시판
```
# 서울특별시 강남구 커뮤니티 게시글 조회
GET /api/board/community/posts/?location_id=1

# 음식 카테고리 커뮤니티 게시글 검색
GET /api/board/community/posts/?category_id=1&search=맛집

# 커뮤니티 인기 게시글 조회
GET /api/board/community/popular/?location_id=1&limit=5
```

### 공공 뉴스 게시판
```
# 서대문구 공공 뉴스 조회
GET /api/board/news/?location_id=5&category=culture

# 서울시 공지사항 조회
GET /api/board/news/?source=seoul&category=notice

# 구청 뉴스만 조회
GET /api/board/news/?source=district
```

## 게시판 구분

### 커뮤니티 게시판 (`/api/board/community/`)
- **특징**: 사용자들이 직접 작성하는 자유로운 소통 공간
- **내용**: 맛집 추천, 지역 정보 공유, 일상 이야기 등
- **관리**: 사용자가 직접 작성, 수정, 삭제
- **권한**: 로그인한 사용자만 작성 가능

### 공공 뉴스 게시판 (`/api/board/news/`)
- **특징**: 공공기관에서 제공하는 공식 정보
- **내용**: 공지사항, 행사 안내, 정책 소식 등
- **관리**: API를 통해 자동 수집, 관리자가 관리
- **권한**: 조회는 누구나 가능, 댓글은 로그인 필요
