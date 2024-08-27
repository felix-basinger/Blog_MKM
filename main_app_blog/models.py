from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)  # Опциональное поле для описания раздела

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    preview = models.TextField(max_length=500, default='No preview available')  # Новое поле для превью
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='post_dislikes', blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_dislikes(self):
        return self.dislikes.count()


class Image(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'Image for {self.post.title}'


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.author.username} на "{self.post.title}"'
