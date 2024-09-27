from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Image, Comment, Tag
from .forms import PostForm, ImageForm, CommentForm
from django_user_agents.utils import get_user_agent


class PostListView(ListView):
    model = Post
    template_name = 'main_app_blog/index.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_template_names(self):
        # Получаем User-Agent объекта из запроса
        user_agent = get_user_agent(self.request)

        # Определяем, является ли устройство мобильным
        if user_agent.is_mobile:
            return ['main_app_blog/mobile/index.html']  # Шаблон для мобильных устройств
        else:
            return ['main_app_blog/index.html']  # Шаблон для десктопов

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()  # Добавляем теги в контекст
        return context


class PopularPostListView(ListView):
    model = Post
    template_name = 'main_app_blog/popular_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_template_names(self):
        # Получаем User-Agent объекта из запроса
        user_agent = get_user_agent(self.request)

        # Определяем, является ли устройство мобильным
        if user_agent.is_mobile:
            return ['main_app_blog/mobile/popular_posts.html']  # Шаблон для мобильных устройств
        else:
            return ['main_app_blog/popular_posts.html']  # Шаблон для десктопов

    def get_queryset(self):
        return Post.objects.order_by('-views')


class LikedPostsListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'main_app_blog/liked_posts.html'  # Указываем шаблон
    context_object_name = 'posts'
    paginate_by = 5

    def test_func(self):
        return not self.request.user.is_staff

    def get_template_names(self):
        # Получаем User-Agent объекта из запроса
        user_agent = get_user_agent(self.request)

        # Определяем, является ли устройство мобильным
        if user_agent.is_mobile:
            return ['main_app_blog/mobile/liked_posts.html']  # Шаблон для мобильных устройств
        else:
            return ['main_app_blog/liked_posts.html']  # Шаблон для десктопов

    def get_queryset(self):
        return Post.objects.filter(likes=self.request.user).order_by('-date_posted')


class TagPostListView(ListView):
    model = Post
    template_name = 'main_app_blog/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_template_names(self):
        user_agent = get_user_agent(self.request)
        if user_agent.is_mobile:
            return ['main_app_blog/mobile/tag_posts.html']
        else:
            return ['main_app_blog/tag_posts.html']

    def get_queryset(self):
        tag = get_object_or_404(Tag, name=self.kwargs.get('tag'))
        return Post.objects.filter(tags=tag).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, name=self.kwargs.get('tag'))
        context['tag'] = tag
        context['tag_description'] = tag.description  # Добавляем описание тега в контекст
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'main_app_blog/post_detail.html'
    context_object_name = 'post'

    def get_template_names(self):
        # Получаем User-Agent объекта из запроса
        user_agent = get_user_agent(self.request)

        # Определяем, является ли устройство мобильным
        if user_agent.is_mobile:
            return ['main_app_blog/mobile/post_detail.html']  # Шаблон для мобильных устройств
        else:
            return ['main_app_blog/post_detail.html']  # Шаблон для десктопов

    def get_object(self, **kwargs):
        post = super().get_object(**kwargs)
        post.views += 1
        post.save()
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return self.get(request, *args, **kwargs)
        return self.render_to_response(self.get_context_data(form=form))


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'main_app_blog/post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['captions'] = ['' for _ in self.request.FILES.getlist('images')]
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        new_tags = form.cleaned_data.get('new_tags')
        if new_tags:
            tag_names = [tag.strip() for tag in new_tags.split(',')]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                form.instance.tags.add(tag)
        removed_tags = form.cleaned_data.get('removed_tags')
        if removed_tags:
            tag_names_to_remove = [tag_name.strip() for tag_name in removed_tags.split(',')]
            for tag_name in tag_names_to_remove:
                tag = Tag.objects.filter(name=tag_name).first()
                if tag:
                    form.instance.tags.remove(tag)
        # Получение контента после его сохранения
        content = form.cleaned_data['content']
        existing_tags = form.cleaned_data.get('tags')
        if existing_tags:
            form.instance.tags.set(existing_tags)
        # Обработка изображений в контенте
        content = self.process_images(content)

        # Сохранение обновленного контента
        self.object.content = content
        self.object.save()

        return response

    def process_images(self, content):
        """
            Обрабатывает изображения в контенте и добавляет к ним подписи.
            """
        images = self.object.images.all()  # Получаем все изображения, связанные с постом
        for image in images:
            # Ищем изображения в контенте по их URL или другим идентификаторам
            image_tag = f'<img src="{image.url}"'
            caption = f'<figcaption>{image.caption}</figcaption>'
        return content


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'main_app_blog/post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['captions'] = [image.caption for image in self.object.images.all()]
        return context

    def form_valid(self, form):
        new_tags = form.cleaned_data.get('new_tags')
        if new_tags:
            tag_names = [tag.strip() for tag in new_tags.split(',')]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                form.instance.tags.add(tag)

        removed_tags = form.cleaned_data.get('removed_tags')
        if removed_tags:
            tag_names_to_remove = [tag_name.strip() for tag_name in removed_tags.split(',')]
            for tag_name in tag_names_to_remove:
                tag = Tag.objects.filter(name=tag_name).first()
                if tag:
                    form.instance.tags.remove(tag)

        form.instance.author = self.request.user
        response = super().form_valid(form)

        existing_tags = form.cleaned_data.get('tags')
        if existing_tags:
            form.instance.tags.set(existing_tags)
        # Получение контента после его сохранения
        content = form.cleaned_data['content']

        # Обработка изображений в контенте и добавление подписей
        content = self.process_images(content)

        # Сохранение обновленного контента
        self.object.content = content
        self.object.save()

        return response

    def process_images(self, content):
        """
            Обрабатывает изображения в контенте и добавляет к ним подписи.
            """
        images = self.object.images.all()  # Получаем все изображения, связанные с постом
        for image in images:
            # Ищем изображения в контенте по их URL или другим идентификаторам
            image_tag = f'<img src="{image.url}"'
            caption = f'<figcaption>{image.caption}</figcaption>'
        return content

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'main_app_blog/post_confirm_delete.html'
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class UserPostListView(ListView):
    model = Post
    template_name = 'main_app_blog/user_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_template_names(self):
        # Получаем User-Agent объекта из запроса
        user_agent = get_user_agent(self.request)

        # Определяем, является ли устройство мобильным
        if user_agent.is_mobile:
            return ['main_app_blog/mobile/user_posts.html']  # Шаблон для мобильных устройств
        else:
            return ['main_app_blog/user_posts.html']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


def about(request):
    user_agent = get_user_agent(request)

    if user_agent.is_mobile:
        template = 'main_app_blog/mobile/about.html'
    else:
        template = 'main_app_blog/about.html'
    return render(request, template, {'title': 'О клубе'})


class CommentDeleteView(View):
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['pk'])
        if request.user == comment.author:
            comment.delete()
            messages.success(request, 'Комментарий успешно удален.')
        else:
            messages.error(request, 'У вас нет прав для удаления этого комментария.')

        return redirect(reverse('post-detail', kwargs={'pk': comment.post.pk}))


@require_POST
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
        if user in post.dislikes.all():
            post.dislikes.remove(user)

    return JsonResponse({'liked': liked, 'total_likes': post.total_likes, 'total_dislikes': post.total_dislikes})


@require_POST
def dislike_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if user in post.dislikes.all():
        post.dislikes.remove(user)
        disliked = False
    else:
        post.dislikes.add(user)
        disliked = True
        if user in post.likes.all():
            post.likes.remove(user)

    return JsonResponse({'disliked': disliked, 'total_likes': post.total_likes, 'total_dislikes': post.total_dislikes})


@require_POST
def delete_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    return JsonResponse({'status': 'success'})
