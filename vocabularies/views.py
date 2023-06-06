
from django.db import IntegrityError
from django.db.models import Q, Sum
from django.db.models import Max

from django.http import HttpResponse
from django.shortcuts import render, redirect

from users.models import User, Admin
from constants import INVALID_KIND

from vocabularies.forms import WordForm, WordForm, ButtonDeleteForm, ButtonDeleteAllForm

from vocabularies.function import TranslateWord, associate, make_picture
from vocabularies.models import Word, VocabularyBooks, Question, WordScore
import datetime
import random

def get_user(request, kind):
    if request.session.get('kind', '') != kind or kind not in {"User", "Admin"}:
        return None

    if len(request.session.get('user', '')) != 10:
        return None

    uid = request.session.get('user')

    if kind == "User":
        number = uid
        User_set = User.objects.filter(client_number=number)
        if User_set.count() == 0:
            return None
        return User_set[0]
    else:
        number = uid
        Admin_set = Admin.objects.filter(admin_number=number)
        if Admin_set.count() == 0:
            return None
        return Admin_set[0]


def home(request, kind):
    if kind == "Admin":
        return Admin_home(request)
    elif kind == "User":
        return User_home(request)
    return HttpResponse(INVALID_KIND)


def Admin_home(request):
    kind = "Admin"
    user = get_user(request, kind)

    if not user:
        return redirect('login', kind=kind)

    info = {
        "name": user.nick_name,
        "kind": kind
    }

    context = {
        "info": info
    }

    return render(request, 'nav.html', context)


def User_home(request):
    kind = "User"
    user = get_user(request, kind)

    if not user:
        return redirect('login', kind=kind)

    info = {
        "name": user.nick_name,
        "kind": kind
    }

    chinese_to_english_form = WordForm()
    english_to_chinese_form = WordForm()
    english_meaning = None
    chinese_meaning = None

    if request.method == 'POST':
        if 'chinese_to_english' in request.POST:
            form = WordForm(request.POST)
            if form.is_valid():
                chinese_meaning = form.cleaned_data['word']
                # 翻译并按行拆分
                s = TranslateWord(chinese_meaning)
                lst = s.splitlines()
                # 获取：后的部分
                s = lst[0]
                lst = s.split("：")
                english_meaning = lst[1]
                # 将单词保存进历史记录里面
                word = chinese_meaning
                language = "Chinese"
                translation = english_meaning
                # 放入code=0的历史记录里面
                book, created = VocabularyBooks.objects.get_or_create(user=user, code="0",
                                                                      defaults={"book_name": "历史记录"})
                new_word = Word(word=word, language=language, book=book, translation=translation)
                try:
                    new_word.save()
                except IntegrityError as e:
                    # 如果违反了唯一约束，则记录日志或执行其他操作
                    print("IntegrityError occurred: ", str(e))

                # 保存到word里
                request.session["word"] = word
                request.session["language"] = language
                request.session["translation"] = translation
        elif 'english_to_chinese' in request.POST:
            form = WordForm(request.POST)
            if form.is_valid():
                english_meaning = form.cleaned_data['word']
                # 翻译并按行拆分
                s = TranslateWord(english_meaning)
                lst = s.splitlines()
                # 获取：后的部分
                s = lst[0]
                lst = s.split("：")
                chinese_meaning = lst[1]
                # 将单词保存进历史记录里面
                word = english_meaning
                language = "English"
                translation = chinese_meaning
                # 放入code=0的历史记录里面
                book, created = VocabularyBooks.objects.get_or_create(user=user, code="0",
                                                                      defaults={"book_name": "历史记录"})
                new_word = Word(word=word, translation=translation, language=language, book=book)
                try:
                    new_word.save()
                except IntegrityError as e:
                    # 如果违反了唯一约束，则记录日志或执行其他操作
                    print("IntegrityError occurred: ", str(e))

                # 保存到word里
                request.session["word"] = word
                request.session["language"] = language
                request.session["translation"] = translation

        elif 'word' in request.POST:
            word = request.session.get("word")
            language = request.session.get("language")
            translation = request.session.get("translation")
            # 放入code=1的收藏里面
            book, created = VocabularyBooks.objects.get_or_create(user=user, code="1",
                                                                  defaults={"book_name": "收藏单词"})
            new_word = Word(word=word, translation=translation, language=language, book=book)
            try:
                new_word.save()
            except IntegrityError as e:
                # 如果违反了唯一约束，则记录日志或执行其他操作
                print("IntegrityError occurred: ", str(e))

    context = {
        "info": info,
        'chinese_to_english_form': chinese_to_english_form,
        'english_to_chinese_form': english_to_chinese_form,
        'english_meaning': english_meaning,
        'chinese_meaning': chinese_meaning
    }

    return render(request, 'home.html', context)


def history(request, *args, **kwargs):
    kind = "User"
    user = get_user(request, kind)

    if not user:
        return redirect('login', kind=kind)

    info = {
        "name": user.nick_name,
        "kind": kind
    }

    delete_form = None
    delete_all_form = None
    if request.method == 'POST':
        if "button_clicked" in request.POST:
            delete_form = ButtonDeleteForm(request.POST)
            if delete_form.is_valid():
                # 删除对应id的单词
                clicked_id = delete_form.cleaned_data['button_clicked']
                clicked_word = Word.objects.get(id=clicked_id)
                clicked_word.delete()
        if "delete_all_history" in request.POST:
            delete_all_form = ButtonDeleteAllForm(request.POST)
            if delete_all_form.is_valid():
                # 删除所有单词
                book = VocabularyBooks.objects.get(user=user, code="0")
                clicked_word = Word.objects.filter(book=book)
                clicked_word.delete()
            else:
                # 返回错误消息
                print(123)
    else:
        delete_form = ButtonDeleteForm()
        delete_all_form = ButtonDeleteAllForm()

    # 查询用户的历史记录
    q = Q(user=user, code="0")
    book = VocabularyBooks.objects.get(q)
    search_list = Word.objects.filter(book=book).order_by('save_day')

    search = {
        "info": info,
        "delete_form": delete_form,
        "delete_all_form": delete_all_form,
        "search_list": search_list
    }
    return render(request, "history.html", search)


def collections(request, *args, **kwargs):
    kind = "User"
    user = get_user(request, kind)

    if not user:
        return redirect('login', kind=kind)

    info = {
        "name": user.nick_name,
        "kind": kind
    }

    form = None
    if request.method == 'POST':
        if "button_clicked" in request.POST:
            form = ButtonDeleteForm(request.POST)
            if form.is_valid():
                # 删除对应id的单词
                clicked_id = form.cleaned_data['button_clicked']
                clicked_word = Word.objects.get(id=clicked_id)
                clicked_word.delete()
        if "delete_all_history" in request.POST:
            form = ButtonDeleteForm(request.POST)
            if form.is_valid():
                # 删除所有单词
                book = VocabularyBooks.objects.get(user=user, code="1")
                clicked_word = Word.objects.filter(book=book)
                clicked_word.delete()
    else:
        form = ButtonDeleteForm()

    # 查询用户的收藏表
    q = Q(user=user, code="1")
    book = VocabularyBooks.objects.get(q)
    collection_list = Word.objects.filter(book=book).order_by('last_day')

    collection = {
        "info": info,
        "form": form,
        "collection_list": collection_list
    }
    return render(request, "collections.html", collection)


def vocabularyTest(request, *args, **kwargs):
    kind = "User"
    user = get_user(request, kind)

    if not user:
        return redirect('login', kind=kind)

    info = {
        "name": user.nick_name,
        "kind": kind
    }

    # 删除所有的问题
    Question.objects.all().delete()

    # 第一步,在收藏表里去寻找5个单词
    book = VocabularyBooks.objects.get(user=user, code="1")
    # 从单词书book中获取5个最远的单词，按照last_day排序
    words = Word.objects.filter(book=book).order_by('-last_day')[:5]
    # 如果不足5个，则选择所有单词
    if len(words) < 5:
        words = Word.objects.filter(book=book)

    # 第二步生成对应的问题
    translation_question = None
    # 遍历每一个单词
    for word in words:
        # 根据语言生成不同的问题描述
        if word.language == "Chinese":
            # 英文翻译
            # synonyms, antonyms, related_words = associate(word.word)
            translation_question = Question(
                question_text="The Chinese meaning of \'" + chinese_translation(word.translation) + "\' is?",
                answer=word.word,
                word=word,
            )
        elif word.language == "English":
            # 中文翻译
            # synonyms, antonyms, related_words = associate(word.translation)
            translation_question = Question(
                question_text='\"'+ english_translation(word.translation) + '\"' + "的英文意思是",
                answer=word.word,
                word=word,
            )

        if word.language == "Chinese":
            # 获取所有的中文单词
            chinese_words = list(Word.objects.filter(book=book, language="Chinese").exclude(word=word.word))
            # 随机选择3个单词作为选项
            choices = random.sample(chinese_words, 3)
            # 将正确答案添加到选项
            choices.append(word)
            # 将选项随机排序
            random.shuffle(choices)
            # 将选项转换成字符串
            choices_str = ",".join([c.word for c in choices])
            # 设置选项信息
            translation_question.choices = choices_str

        elif word.language == "English":
            # 获取所有的英文单词
            english_words = list(Word.objects.filter(book=book, language="English").exclude(word=word.word))
            # 随机选择三个单词作为选项
            choices = random.sample(english_words, 3)
            # 将正确答案添加到选项
            choices.append(word)
            # 将选项随机排序
            random.shuffle(choices)
            # 将选项转换成字符串
            choices_str = ",".join([c.word for c in choices])
            # 设置选项信息
            translation_question.choices = choices_str

        # 将生成的问题保存到数据库中
        translation_question.save()

    questions = Question.objects.order_by('id')
    context = {'questions': questions}
    for question in questions:
        if question.choices:
            question.choice_list = question.choices.split(',')
    context["info"] = info
    return render(request, 'question_index.html', context)


def check(request):
    kind = "User"
    user = get_user(request, kind)

    if not user:
        return redirect('login', kind=kind)

    info = {
        "name": user.nick_name,
        "kind": kind
    }

    score = 0
    # 查找所有的WordScore
    word_scores = WordScore.objects.all()
    # 返回最大times
    max_times = word_scores.aggregate(Max('times'))['times__max'] or 0
    for question in Question.objects.order_by('id'):
        user_answer = request.POST.get(str(question.id))
        get_score = 0
        if user_answer == question.answer:
            score += 1
            get_score = 1

        word = question.word
        # 创建新的WordScore实例
        new_word_score = WordScore.objects.create(score=get_score, times=max_times + 1, word=word)
        new_word_score.save()

    context = {'score': score}
    context["info"] = info
    return render(request, 'check.html', context)


def chinese_translation(translation):
    list = translation.split(";")
    trans = random.choice(list)
    return trans


def english_translation(translation):
    list = translation.split(";")
    trans = random.choice(list)
    return trans


def show_score(request, *args, **kwargs):
    # 查找所有的WordScore
    word_scores = WordScore.objects.all()
    # 返回最大times
    max_times = word_scores.aggregate(Max('times'))['times__max'] or 0
    print(max_times)
    # 遍历times并计算score之和
    score_sums = []
    for i in range(1, max_times + 1):
        scores = word_scores.filter(times=i)
        score_sum = scores.aggregate(Sum('score'))['score__sum'] or 0
        score_sums.append(score_sum)

    # img_url = "/static/img/first.png"
    img_url = make_picture(score_sums)
    return render(request, "scores.html", {"img_url": img_url})
