from django import forms
from .models import PhotoUpload, ReceiptOCR, Recipe, Post
import os


class PhotoUploadForm(forms.ModelForm):
    """테이블1: 사진 업로드 폼"""
    class Meta:
        model = PhotoUpload
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png',
            })
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # 파일 크기 검증 (5MB = 5 * 1024 * 1024 bytes)
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise forms.ValidationError(
                    f'파일 크기는 5MB를 초과할 수 없습니다. (현재: {image.size / 1024 / 1024:.2f}MB)'
                )
            
            # 파일 확장자 검증 (안전한 방법)
            valid_extensions = ['jpg', 'jpeg', 'png']
            ext = os.path.splitext(image.name)[1].lower().replace('.', '')
            
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'JPG, JPEG, PNG 파일만 업로드 가능합니다. (현재: .{ext})'
                )
        
        return image


class ReceiptOCRForm(forms.ModelForm):
    """테이블2: 영수증 OCR 폼"""
    class Meta:
        model = ReceiptOCR
        fields = ['receipt_image']
        widgets = {
            'receipt_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            })
        }
    
    def clean_receipt_image(self):
        image = self.cleaned_data.get('receipt_image')
        
        if image:
            # 파일 크기 검증 (10MB)
            max_size = 10 * 1024 * 1024
            if image.size > max_size:
                raise forms.ValidationError('영수증 이미지는 10MB를 초과할 수 없습니다.')
        
        return image


class RecipeForm(forms.ModelForm):
    """테이블3: 레시피 폼 (300자 제한)"""
    class Meta:
        model = Recipe
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '레시피 제목을 입력하세요',
                'maxlength': 100,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '레시피 내용을 입력하세요 (최대 300자)',
                'maxlength': 300,
                'rows': 6,
                'id': 'recipe-content',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if len(content) > 300:
            raise forms.ValidationError(
                f'레시피 내용은 300자를 초과할 수 없습니다. (현재: {len(content)}자)'
            )
        if len(content.strip()) == 0:
            raise forms.ValidationError('레시피 내용을 입력해주세요.')
        return content
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if len(title.strip()) == 0:
            raise forms.ValidationError('레시피 제목을 입력해주세요.')
        return title


class PostForm(forms.ModelForm):
    """테이블4: 게시글 폼 (200자 제한)"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요',
                'maxlength': 100,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '내용을 입력하세요 (최대 200자)',
                'maxlength': 200,
                'rows': 5,
                'id': 'post-content',
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-select',
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if len(content) > 200:
            raise forms.ValidationError(
                f'게시글 내용은 200자를 초과할 수 없습니다. (현재: {len(content)}자)'
            )
        if len(content.strip()) == 0:
            raise forms.ValidationError('게시글 내용을 입력해주세요.')
        return content
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if len(title.strip()) == 0:
            raise forms.ValidationError('게시글 제목을 입력해주세요.')
        return title