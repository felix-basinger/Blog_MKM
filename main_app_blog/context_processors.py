from .models import Tag


def tags_processor(request):
    tags = Tag.objects.all()
    return {'tags': tags}
