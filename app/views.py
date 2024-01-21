import math

from django.contrib import auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.urls import reverse

from app.forms import LoginForm, RegisterForm, SettingsForm, QuestionForm, AddAnswerForm
from app.models import *

QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'content': f'''Lorem Ipsum is simply dummy text of the printing and typesetting
            industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
            when an unknown printer took a galley of type and scrambled it to make a type specimen
            book.''',
        'tags': ['python', 'programming', 'askme'],
        'answers': [
            {
                'id': i,
                'content': f'''First of all I would like to thank you for the invitation to participate in such a
                Russia is the huge territory which in many respects needs to be render habitable. {i}'''
            } for i in range(50)
        ]
    } for i in range(100)
]


def paginate(request, objects, per_page=15):
    result = None
    first = end = 1
    num_page = 1
    pages_pagination = []
    try:
        page = request.GET.get('page', 1)

        paginator = Paginator(objects, per_page)
        result = paginator.page(page)

        num_page = int(page)
    except Exception as e:
        print(e)

    all_pages = math.ceil(len(objects) / per_page)

    i = num_page
    count = 0
    if i < all_pages:
        while count < 3:
            pages_pagination.append(i)
            i += 1
            if i == all_pages:
                break
            count += 1

    if num_page == 1:
        first = None
    if num_page == all_pages:
        end = None

    return (result, {
        "first": first,
        "end": end,
        "enditem": all_pages,
        "items": pages_pagination
    })


def add_image_profile(user, request):
    file = request.FILES['image']
    fs = FileSystemStorage()
    filename = fs.save("user_" + str(user.id) + "/avatar." + str(file.name).split(".")[1], file)
    profile = Profile.objects.get_or_create(user=user)[0]
    profile.image = filename
    profile.save()


@login_required(login_url='login/', redirect_field_name='continue')
def index(request):
    questions = Question.objects.new()
    page_items, pagination = paginate(request, questions, 10)

    return render(
        request,
        'index.html',
        {
            'questions': page_items,
            'pages': pagination
        }
    )


def hot(request):
    hot_questions = Question.objects.hot()
    page_items, pagination = paginate(request, hot_questions, 10)

    return render(request, 'hot.html', {
        'questions': page_items,
        'pages': pagination
    })


def tag(request, tag_name):
    tag_questions = Tag.objects.get(tag_name=tag_name).questions.all()
    page_items, pagination = paginate(request, tag_questions, 10)

    return render(request, 'tag_listing.html', {
        'tag': tag_name,
        'questions': page_items,
        'pages': pagination
    })


def question(request, question_id):
    item = get_object_or_404(Question, id=question_id)

    answers, pagination = paginate(request, item.answers, 10)

    if request.method == 'GET':
        form = AddAnswerForm()
    if request.method == "POST":
        form = AddAnswerForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                current_user = request.user
                user = User.objects.get(username=current_user.username).profile

                data = form.cleaned_data
                Answer.objects.create(author=user, question=item, text=data["answer"], accepted=False)

                # Получение ID последнего созданного ответа
                last_answer_id = Answer.objects.latest('id').id

                # Формирование URL для редиректа
                redirect_url = f'/question/{question_id}?page={pagination["enditem"]}#{last_answer_id}'

                # Редирект на новый ответ
                return redirect(redirect_url)
            else:
                form.add_error('answer', "You must be logged in!")

    return render(request, 'question.html', {
        'question': item,
        'pagination_answers': answers,
        'pages': pagination,
        'form': form
    })


def log_in(request):
    if request.method == 'GET':
        form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(request.GET.get('continue', '/'))
                else:
                    form.add_error('username', "Your account is not active")
            else:
                form.add_error(None, "Wrong password or user doesn't exist")

    return render(
        request,
        'login.html', context={"form": form}
    )


def log_out(request):
    auth.logout(request)
    return redirect(reverse('login'))


def signup(request):
    if request.method == 'GET':
        form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            user = User.objects.get(username=new_user.username)
            if request.FILES:
                add_image_profile(user, request)
            login(request, new_user)
            return redirect(reverse('index'))

    return render(
        request,
        'signup.html', context={"form": form}
    )


def ask(request):
    if request.method == 'GET':
        form = QuestionForm()
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if request.user.is_authenticated:
                current_user = request.user

                user = User.objects.get(username=current_user.username).profile

                post_question = Question.objects.create(title=data["title"], content=data["content"],
                                                        author=user)

                # добавление лайка
                # user_obj = User.objects.get(username=request.user)
                # question_model_type = ContentType.objects.get_for_model(post_question)
                # Like.objects.create(content_type=question_model_type, object_id=post_question.id, user=user_obj)

                tags = str(data["tags"]).split(" ")
                for elem in tags:
                    tag_elem = Tag.objects.get_or_create(tag_name=elem)
                    post_question.tags.add(tag_elem[0].id)

                return redirect(question, question_id=post_question.id)
            else:
                form.add_error('title', "You must be logged in!")

    return render(
        request,
        'ask.html',
        {"form": form}
    )


def settings(request):
    current_user = request.user
    if request.method == 'GET':
        profile = User.objects.get(username=current_user.username).profile
        form = SettingsForm(initial={'username': profile.user.username, 'first_name': profile.user.first_name,
                                     'email': profile.user.email,
                                     })
    if request.method == "POST":
        form = SettingsForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.get(username=current_user.username)
            user.username = data["username"]
            user.first_name = data["first_name"]
            user.email = data["email"]
            user.save()
            if request.FILES:
                add_image_profile(user, request)

    return render(
        request,
        'settings.html', context={"form": form}
    )