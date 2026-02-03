from django.urls import path
from . import views

app_name = 'homecook'

urlpatterns = [
    # 최초 메인 페이지
    path('', views.HomeView.as_view(), name='home'),
    
    # 나의 챌린지 (로그인 후 메인)
    path('my-challenge/', views.MyChallengeView.as_view(), name='my_challenge'),
    
    # 글 생성 선택 (4가지 옵션)
    path('create/', views.CreateSelectView.as_view(), name='create_select'),
    
    # 테이블1: 사진 업로드
    path('photos/', views.HomecookIndexView.as_view(), name='photo_list'),
    path('photo/create/', views.HomecookCreateView.as_view(), name='photo_create'),
    path('photo/<int:pk>/update/', views.HomecookUpdateView.as_view(), name='photo_update'),
    path('photo/<int:pk>/delete/', views.HomecookDeleteView.as_view(), name='photo_delete'),
    
    # 테이블2: 영수증 OCR
    path('receipt/', views.ReceiptListView.as_view(), name='receipt_list'),
    path('receipt/create/', views.ReceiptCreateView.as_view(), name='receipt_create'),
    path('receipt/<int:pk>/', views.ReceiptDetailView.as_view(), name='receipt_detail'),
    
    # 테이블3: 레시피
    path('recipe/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipe/create/', views.RecipeCreateView.as_view(), name='recipe_create'),
    path('recipe/<int:pk>/update/', views.RecipeUpdateView.as_view(), name='recipe_update'),
    path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
    
    # 테이블4: 게시글
    path('post/', views.PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
]
