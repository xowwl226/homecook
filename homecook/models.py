from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models import F


class PhotoUpload(models.Model):
    """테이블1: 사진 업로드"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    image = models.ImageField(
        upload_to='photos/%Y/%m/%d/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        verbose_name='사진',
        help_text='5MB 이하, 1000x1000 픽셀'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')
    
    class Meta:
        verbose_name = '사진 업로드'
        verbose_name_plural = '사진 업로드'
        ordering = ['-uploaded_at']
    
    def save(self, *args, **kwargs):
        """이미지 리사이징 처리"""
        if self.image and hasattr(self.image, 'file'):
            from PIL import Image
            from io import BytesIO
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import sys
            
            try:
                # 이미지 열기
                img = Image.open(self.image)
                
                # RGB로 변환 (투명도 제거)
                if img.mode in ('RGBA', 'P', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 1000x1000 리사이징 (비율 유지)
                if img.width > 1000 or img.height > 1000:
                    img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                
                # BytesIO에 저장
                output = BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                # 파일명 정리 (확장자를 .jpg로 통일)
                import os
                original_name = os.path.splitext(self.image.name)[0]
                
                # 파일 교체
                self.image = InMemoryUploadedFile(
                    output,
                    'ImageField',
                    f"{original_name}.jpg",
                    'image/jpeg',
                    sys.getsizeof(output),
                    None
                )
            except Exception as e:
                # 이미지 처리 실패시 원본 그대로 저장
                pass
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class ReceiptOCR(models.Model):
    """테이블2: 영수증 OCR"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    receipt_image = models.ImageField(
        upload_to='receipts/%Y/%m/%d/',
        verbose_name='영수증 이미지'
    )
    ocr_text = models.TextField(blank=True, verbose_name='OCR 추출 텍스트')
    processed_at = models.DateTimeField(auto_now_add=True, verbose_name='처리일시')
    is_processed = models.BooleanField(default=False, verbose_name='처리완료')
    
    class Meta:
        verbose_name = '영수증 OCR'
        verbose_name_plural = '영수증 OCR'
        ordering = ['-processed_at']
    
    def process_ocr(self):
        """OCR 처리 실행"""
        try:
            from PIL import Image
            import pytesseract
            
            # 이미지 열기
            img = Image.open(self.receipt_image.path)
            
            # OCR 실행 (한국어 + 영어)
            ocr_text = pytesseract.image_to_string(img, lang='kor+eng')
            
            # 결과 저장
            self.ocr_text = ocr_text.strip()
            self.is_processed = True
            self.save()
            
            return True
        except ImportError:
            # pytesseract 미설치시 임시 텍스트
            self.ocr_text = "[OCR 라이브러리 미설치]\npip install pytesseract 필요\nTesseract-OCR 엔진 설치 필요"
            self.is_processed = False
            self.save()
            return False
        except Exception as e:
            self.ocr_text = f"OCR 처리 중 오류: {str(e)}"
            self.is_processed = False
            self.save()
            return False
    
    def __str__(self):
        return f"{self.user.username} - {self.processed_at.strftime('%Y-%m-%d')}"


class Recipe(models.Model):
    """테이블3: 나의 레시피 (공개형, 300자)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    title = models.CharField(max_length=100, verbose_name='레시피 제목')
    content = models.TextField(max_length=300, verbose_name='레시피 내용')
    image = models.ImageField(
        upload_to='recipes/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='레시피 사진'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    views = models.PositiveIntegerField(default=0, verbose_name='조회수')
    
    class Meta:
        verbose_name = '레시피'
        verbose_name_plural = '레시피'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """조회수 증가 (Race Condition 방지)"""
        Recipe.objects.filter(pk=self.pk).update(views=F('views') + 1)


class Post(models.Model):
    """테이블4: 게시글 (공개/비공개, 200자)"""
    VISIBILITY_CHOICES = [
        ('public', '공개'),
        ('private', '비공개'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자')
    title = models.CharField(max_length=100, verbose_name='제목')
    content = models.TextField(max_length=200, verbose_name='내용')
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public',
        verbose_name='공개여부'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '게시글'
        verbose_name_plural = '게시글'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]
    
    def __str__(self):
        return f"[{self.get_visibility_display()}] {self.title}"