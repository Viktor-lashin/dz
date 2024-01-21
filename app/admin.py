from django.contrib import admin
from app.models import Profile, Question, Answer, Tag, Like

# Register your models here.
admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Like)