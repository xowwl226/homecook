from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import PhotoUpload, ReceiptOCR, Recipe, Post
from .forms import PhotoUploadForm, ReceiptOCRForm, RecipeForm, PostForm
from django.contrib import messages
from django.views.generic import TemplateView



# ========== 메인 페이지 ==========
class HomeView(TemplateView):
    """최초 메인 페이지 (로그인 불필요)"""
    template_name = 'homecook/home.html'


# ========== 나의 챌린지 ==========
class MyChallengeView(LoginRequiredMixin, generic.ListView):
    """나의 챌린지 - 오늘의 집 콕 목록"""
    model = Recipe  # 임시로 Recipe 사용
    template_name = 'homecook/my_challenge.html'
    context_object_name = 'challenges'
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        # 최근 8개의 아이템 표시
        return Recipe.objects.all()[:8]


# ========== 글 생성 선택 페이지 ==========
class CreateSelectView(LoginRequiredMixin, TemplateView):
    """글 생성 옵션 선택 페이지"""
    template_name = 'homecook/create_select.html'
    login_url = '/accounts/login/'



# ========== 테이블1: 사진 업로드 ==========
class HomecookIndexView(LoginRequiredMixin, generic.ListView):
    """사진 목록 조회"""
    model = PhotoUpload
    template_name = 'homecook/photo_list.html'
    context_object_name = 'photos'
    paginate_by = 12
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return PhotoUpload.objects.filter(user=self.request.user)


class HomecookCreateView(LoginRequiredMixin, generic.CreateView):
    """사진 업로드"""
    model = PhotoUpload
    form_class = PhotoUploadForm
    template_name = 'homecook/photo_form.html'
    success_url = reverse_lazy('homecook:index')
    login_url = '/accounts/login/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '사진이 성공적으로 업로드되었습니다.')
        return super().form_valid(form)


class HomecookUpdateView(LoginRequiredMixin, generic.UpdateView):
    """사진 수정"""
    model = PhotoUpload
    form_class = PhotoUploadForm
    template_name = 'homecook/photo_form.html'
    success_url = reverse_lazy('homecook:index')
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return PhotoUpload.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, '사진이 수정되었습니다.')
        return super().form_valid(form)


class HomecookDeleteView(LoginRequiredMixin, generic.DeleteView):
    """사진 삭제"""
    model = PhotoUpload
    template_name = 'homecook/photo_confirm_delete.html'
    success_url = reverse_lazy('homecook:index')
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return PhotoUpload.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '사진이 삭제되었습니다.')
        return super().delete(request, *args, **kwargs)


# ========== 테이블2: 영수증 OCR ==========
class ReceiptListView(LoginRequiredMixin, generic.ListView):
    """영수증 목록"""
    model = ReceiptOCR
    template_name = 'homecook/receipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 10
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return ReceiptOCR.objects.filter(user=self.request.user)


class ReceiptCreateView(LoginRequiredMixin, generic.CreateView):
    """영수증 업로드 및 OCR 처리"""
    model = ReceiptOCR
    form_class = ReceiptOCRForm
    template_name = 'homecook/receipt_form.html'
    success_url = reverse_lazy('homecook:receipt_list')
    login_url = '/accounts/login/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # OCR 처리 실행
        success = self.object.process_ocr()
        
        if success:
            messages.success(self.request, 'OCR 처리가 완료되었습니다.')
        else:
            messages.warning(self.request, 'OCR 처리 중 문제가 발생했습니다. 상세 내용을 확인해주세요.')
        
        return response


class ReceiptDetailView(LoginRequiredMixin, generic.DetailView):
    """영수증 상세 (OCR 결과 확인)"""
    model = ReceiptOCR
    template_name = 'homecook/receipt_detail.html'
    context_object_name = 'receipt'
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return ReceiptOCR.objects.filter(user=self.request.user)


# ========== 테이블3: 레시피 ==========
class RecipeListView(generic.ListView):
    """레시피 목록 (공개)"""
    model = Recipe
    template_name = 'homecook/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 12


class RecipeDetailView(generic.DetailView):
    """레시피 상세"""
    model = Recipe
    template_name = 'homecook/recipe_detail.html'
    context_object_name = 'recipe'
    
    def get_object(self):
        obj = super().get_object()
        # 조회수 증가 (Race Condition 방지)
        obj.increment_views()
        obj.refresh_from_db()
        return obj


class RecipeCreateView(LoginRequiredMixin, generic.CreateView):
    """레시피 작성"""
    model = Recipe
    form_class = RecipeForm
    template_name = 'homecook/recipe_form.html'
    success_url = reverse_lazy('homecook:recipe_list')
    login_url = '/accounts/login/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '레시피가 등록되었습니다.')
        return super().form_valid(form)


class RecipeUpdateView(LoginRequiredMixin, generic.UpdateView):
    """레시피 수정"""
    model = Recipe
    form_class = RecipeForm
    template_name = 'homecook/recipe_form.html'
    success_url = reverse_lazy('homecook:recipe_list')
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, '레시피가 수정되었습니다.')
        return super().form_valid(form)


class RecipeDeleteView(LoginRequiredMixin, generic.DeleteView):
    """레시피 삭제"""
    model = Recipe
    template_name = 'homecook/recipe_confirm_delete.html'
    success_url = reverse_lazy('homecook:recipe_list')
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '레시피가 삭제되었습니다.')
        return super().delete(request, *args, **kwargs)


# ========== 테이블4: 게시글 ==========
class PostListView(generic.ListView):
    """게시글 목록"""
    model = Post
    template_name = 'homecook/post_list.html'
    context_object_name = 'posts'
    paginate_by = 15
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 로그인 사용자: 자신의 모든 글 + 타인의 공개글
            from django.db.models import Q
            return Post.objects.filter(
                Q(user=self.request.user) | Q(visibility='public')
            ).select_related('user')
        else:
            # 비로그인 사용자: 공개글만
            return Post.objects.filter(visibility='public').select_related('user')


class PostDetailView(generic.DetailView):
    """게시글 상세"""
    model = Post
    template_name = 'homecook/post_detail.html'
    context_object_name = 'post'
    
    def get_object(self):
        obj = super().get_object()
        
        # 비공개 글 권한 체크
        if obj.visibility == 'private':
            if not self.request.user.is_authenticated or obj.user != self.request.user:
                raise PermissionDenied("이 게시글은 비공개입니다.")
        
        return obj


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    """게시글 작성"""
    model = Post
    form_class = PostForm
    template_name = 'homecook/post_form.html'
    success_url = reverse_lazy('homecook:post_list')
    login_url = '/accounts/login/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '게시글이 등록되었습니다.')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
    """게시글 수정"""
    model = Post
    form_class = PostForm
    template_name = 'homecook/post_form.html'
    success_url = reverse_lazy('homecook:post_list')
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, '게시글이 수정되었습니다.')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    """게시글 삭제"""
    model = Post
    template_name = 'homecook/post_confirm_delete.html'
    success_url = reverse_lazy('homecook:post_list')
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '게시글이 삭제되었습니다.')
        return super().delete(request, *args, **kwargs)

