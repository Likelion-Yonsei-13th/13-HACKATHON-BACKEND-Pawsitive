from django.urls import path
from .views import (
    # 메인 화면
    main_view,
    # API Views - 공공 데이터 소식
    public_data_list_view, public_data_category_counts_view, public_data_urgent_alerts_view,
    # API Views - 제보 데이터 소식
    report_data_list_view, report_data_category_counts_view, report_data_urgent_news_view,
    # API Views - 댓글
    report_data_comments_view, report_data_comment_create_view,
    # API Views - 신고
    report_data_report_create_view, user_reports_view,
    # API Views - 지역행사 (기존 유지)
    local_event_list_view, local_event_detail_view, local_event_comment_create_view,
    local_event_like_view, local_event_interest_view, event_subscription_view,
    update_events_view, local_event_featured_view,
    # Web Views - 공공 데이터 소식
    public_data_view, public_data_category_view, public_data_detail_view_web,
    # Web Views - 제보 데이터 소식
    report_data_view, report_data_category_view, report_data_detail_view_web,
    report_data_category_view_web, report_data_create_view_web,
    # Web Views - 지역행사 (기존 유지)
    local_event_board_view, local_event_detail_view_web,
    # 마이페이지
    mypage_view, mypage_profile_view, mypage_notifications_view, mypage_customer_center_view, mypage_withdrawal_view, myregion_view, myinterests_view,
    # 나의 지역 관련
    myregion_residence_view, myregion_interests_view, myregion_add_view,
    # 나의 관심 행사/상권 관련
    myinterests_categories_view, myinterests_scraps_view, myinterests_change_view,
    # API Views - 제보 데이터 생성
    report_data_create_api_view
)

urlpatterns = [
    # 웹 페이지 URLs - 공공 데이터 소식
    path('public-data/', public_data_view, name='public-data-web'),
    path('public-data/category/<str:category>/', public_data_category_view, name='public-data-category-web'),
    path('public-data/<int:alert_id>/', public_data_detail_view_web, name='public-data-detail-web'),
    
    # 웹 페이지 URLs - 제보 데이터 소식
    path('report-data/', report_data_view, name='report-data-web'),
    path('report-data/category/<str:category>/', report_data_category_view_web, name='report-data-category-web'),
    path('report-data/<int:news_id>/', report_data_detail_view_web, name='report-data-detail-web'),
    path('report-data/create/', report_data_create_view_web, name='report-data-create-web'),
    
    # 웹 페이지 URLs - 지역행사 (기존 유지)
    path('events/', local_event_board_view, name='event-board-web'),
    path('events/<int:event_id>/', local_event_detail_view_web, name='event-detail-web'),
    
    # 마이페이지 URLs
    path('mypage/', mypage_view, name='mypage'),
    path('mypage/profile/', mypage_profile_view, name='mypage-profile'),
    path('mypage/notifications/', mypage_notifications_view, name='mypage-notifications'),
    path('mypage/customer-center/', mypage_customer_center_view, name='mypage-customer-center'),
    path('mypage/withdrawal/', mypage_withdrawal_view, name='mypage-withdrawal'),
    path('myregion/', myregion_view, name='myregion'),
    path('myregion/residence/', myregion_residence_view, name='myregion-residence'),
    path('myregion/interests/', myregion_interests_view, name='myregion-interests'),
    path('myregion/add/', myregion_add_view, name='myregion-add'),
    path('myinterests/', myinterests_view, name='myinterests'),
    path('myinterests/categories/', myinterests_categories_view, name='myinterests-categories'),
    path('myinterests/scraps/', myinterests_scraps_view, name='myinterests-scraps'),
    path('myinterests/change/', myinterests_change_view, name='myinterests-change'),
    
    # API URLs - 공공 데이터 소식
    path('public-data/', public_data_list_view, name='public-data-list'),
    path('public-data/category-counts/', public_data_category_counts_view, name='public-data-category-counts'),
    path('public-data/urgent-alerts/', public_data_urgent_alerts_view, name='public-data-urgent-alerts'),
    
    # API URLs - 제보 데이터 소식
    path('report-data/', report_data_list_view, name='report-data-list'),
    path('report-data/category-counts/', report_data_category_counts_view, name='report-data-category-counts'),
    path('report-data/urgent-news/', report_data_urgent_news_view, name='report-data-urgent-news'),
    path('report-data/create/', report_data_create_api_view, name='report-data-create-api'),
    
    # API URLs - 댓글
    path('report-data/<int:news_id>/comments/', report_data_comments_view, name='report-data-comments'),
    path('report-data/<int:news_id>/comments/create/', report_data_comment_create_view, name='report-data-comment-create'),
    
    # API URLs - 신고
    path('report-data/<int:news_id>/report/', report_data_report_create_view, name='report-data-report-create'),
    path('user/reports/', user_reports_view, name='user-reports'),
    
    # API URLs - 지역행사 (기존 유지)
    path('events/', local_event_list_view, name='local-event-list'),
    path('events/<int:event_id>/', local_event_detail_view, name='local-event-detail'),
    path('events/<int:event_id>/comments/', local_event_comment_create_view, name='local-event-comment-create'),
    path('events/<int:event_id>/like/', local_event_like_view, name='local-event-like'),
    path('events/<int:event_id>/interest/', local_event_interest_view, name='local-event-interest'),
    path('events/subscription/', event_subscription_view, name='event-subscription'),
    path('events/update/', update_events_view, name='update-events'),
    path('events/featured/', local_event_featured_view, name='local-event-featured'),
]
