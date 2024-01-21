from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count


class QuestionManager(models.Manager):
    def hot(self):
        return self.annotate(num_likes=Count('likes')).order_by('-num_likes', '-created')

    def new(self):
        return self.order_by("-created")

    def by_tag(self, tag_name):
        return self.filter(tags__tag_name=tag_name).distinct()

    def by_tags(self, tag_names):
        return self.filter(tags__tag_name__in=tag_names).distinct()


def user_directory_path(instance, filename):
    return 'user_{0}/ {1}'.format(instance.user.id, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    image = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True
    )


class Tag(models.Model):
    tag_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return f"{self.tag_name}"


class Like(models.Model):
    user = models.ForeignKey(User,
                             related_name='likes',
                             on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Question(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    tags = models.ManyToManyField('Tag', related_name='questions')
    likes = GenericRelation(Like)

    title = models.CharField(max_length=256)
    content = models.CharField(max_length=3000)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = QuestionManager()

    @property
    def rating(self):
        return self.likes.count()

    @property
    def answers(self):
        return self.answer_set.all()

    @property
    def answers_count(self):
        return self.answer_set.count()


class Answer(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    likes = GenericRelation(Like)

    text = models.CharField(max_length=3000, null=False, blank=False)
    accepted = models.BooleanField(default=False)

    @property
    def rating(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.author.user.first_name} answer"
