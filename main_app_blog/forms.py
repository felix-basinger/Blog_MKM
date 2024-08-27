from django import forms
from .models import Post, Image, Comment, Tag
from django_summernote.widgets import SummernoteWidget


class PostForm(forms.ModelForm):
    current_tags = forms.CharField(
        label="Розділи посту:",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Виберіть розділи для посту:"
    )

    new_tags = forms.CharField(
        max_length=100,
        required=False,
        label="Додати нові розділи:",
        help_text="Введіть розділи через кому"
    )
    new_tags_description = forms.CharField(
        max_length=500,
        required=False,
        label="Опис нових розділів:",
        help_text="Введіть описи через / відповідно до порядку введених розділів",
        widget=forms.Textarea(attrs={'rows': 3})
    )

    removed_tags = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=""
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Если это существующий пост, заполняем поле current_tags
            self.fields['current_tags'].initial = ', '.join([tag.name for tag in self.instance.tags.all()])

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Обработка новых тегов и описаний
        new_tags = self.cleaned_data.get('new_tags', '')
        new_tags_description = self.cleaned_data.get('new_tags_description', '').split('/')

        if new_tags:
            tag_names = [tag.strip() for tag in new_tags.split(',')]
            for i, tag_name in enumerate(tag_names):
                description = new_tags_description[i].strip() if i < len(new_tags_description) else ''
                tag, created = Tag.objects.get_or_create(name=tag_name)
                if created:
                    tag.description = description
                else:
                    # Если тег уже существует, обновляем его описание
                    tag.description = description
                tag.save()  # Обязательно сохраняем изменения
                instance.tags.add(tag)

        if commit:
            instance.save()

        return instance

    class Meta:
        model = Post
        fields = ['title', 'preview', 'content']
        labels = {
            'title': 'Заголовок',
            'preview': 'Превью',
            'content': 'Зміст',
        }
        widgets = {
            'content': SummernoteWidget(attrs={
                'summernote': {
                    'styleWithSpan': False,
                    'height': 600,
                    'width': '100%',
                    'toolbar': [
                        ['style', ['bold', 'italic', 'underline', 'clear']],
                        ['fontname', ['fontname']],  # Добавление выбора шрифта
                        ['font', ['strikethrough', 'superscript', 'subscript']],
                        ['fontsize', ['fontsize']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol', 'paragraph']],
                        ['height', ['height']],
                        ['insert', ['picture', 'link', 'video', 'table', 'hr']],
                    ],
                    'callbacks': {
                        'onImageUpload': '''function(files) {
                            var editor = $(this);
                            var data = new FormData();
                            data.append("file", files[0]);
                            $.ajax({
                                url: '/upload_image/',
                                method: 'POST',
                                data: data,
                                contentType: false,
                                processData: false,
                                success: function(url) {
                                    editor.summernote('insertImage', url, function($image) {
                                        $image.css('width', '100%');
                                        $image.css('height', 'auto');
                                        $image.css('object-fit', 'cover');
                                        $image.css('border-radius', '15px');
                                    });
                                }
                            });
                        }'''
                    }
                }
            })
        }


class ImageForm(forms.ModelForm):
    caption = forms.CharField(required=False, label='Подпись к изображению')

    class Meta:
        model = Image
        fields = ['image', 'caption']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
