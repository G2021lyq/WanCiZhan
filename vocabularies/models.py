from django.db import models
import datetime

from users.models import User


def current_year():
    # refer: https://stackoverflow.com/questions/49051017/year-field-in-django/49051348
    return datetime.date.today().year


def current_day():
    return datetime.date.today()


# 单词书
class VocabularyBooks(models.Model):
    # 名字和代码用来标识单词书
    book_name = models.CharField(max_length=50, verbose_name="单词书名称")
    code = models.CharField(max_length=10, verbose_name="单词书对应代码")

    # 外键用户，当用户被删除，单词书也被删除。
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)

    class Meta:
        # 定义约束条件，保证user+code一定不一样
        constraints = [
            models.UniqueConstraint(fields=['user', 'code'], name='user_code')
        ]

    def __str__(self):
        return "%s(编号为:%s)" % (self.book_name, self.code)


# 单词
class Word(models.Model):
    languages = [
        ("Chinese", "中文"),
        ("English", "英语")
    ]
    # 保存的单词和语言
    word = models.CharField(max_length=50, verbose_name="词语")
    translation = models.CharField(max_length=200, verbose_name="翻译")
    language = models.CharField(max_length=30, verbose_name="语言", choices=languages)
    # 保存的时间
    save_day = models.DateField(verbose_name="保存时间", default=datetime.date.today)
    # 上一次学习的时间
    last_day = models.DateField(verbose_name="上次时间", default=datetime.date.today)

    # 外键单词书，当单词书被删除，单词被删除
    book = models.ForeignKey(VocabularyBooks, verbose_name="单词书", on_delete=models.CASCADE)

    class Meta:
        # 定义约束条件，保证word+language+book一定不一样
        constraints = [
            models.UniqueConstraint(fields=['word', 'language', 'book'], name='book_word')
        ]

    def __str__(self):
        return "%s %s" % (self.languages, self.word)


# 单词测试问题
class Question(models.Model):
    # 问题描述
    question_text = models.CharField(max_length=200, verbose_name="问题描述")
    # 正确答案
    answer = models.CharField(max_length=200, verbose_name="正确答案")
    # 选项信息
    choices = models.CharField(max_length=200, blank=True, verbose_name="选项信息")

    # 外键单词。如果单词被删除了，那么问题也会被删除
    word = models.ForeignKey(Word, verbose_name="单词", on_delete=models.CASCADE)

    # 无需定义约束

    def __str__(self):
        return self.question_text


# 单词得分
class WordScore(models.Model):
    # 单词测试得分、第几次测试
    score = models.IntegerField(verbose_name="得分")
    times = models.IntegerField(verbose_name="次数", default=1)

    # 外键单词，当单词被删除，单词得分被删除。
    word = models.ForeignKey(Word, verbose_name="单词", on_delete=models.CASCADE)

    class Meta:
        # 定义约束条件，保证word+times一定不一样
        constraints = [
            models.UniqueConstraint(fields=['word', 'times'], name='word_times')
        ]

    def __str__(self):
        return "%s %s" % (self.score, self.times)


# 单词学习时间
class WordTime(models.Model):
    time = models.CharField(max_length=20, verbose_name="学习的时间")
    # 外键单词
    word = models.ForeignKey(Word, verbose_name="单词", on_delete=models.CASCADE)

    class Meta:
        # 定义约束条件，保证word+time一定不一样
        constraints = [
            models.UniqueConstraint(fields=['word', 'time'], name='word_time')
        ]

    def __str__(self):
        return "%s %s" % (self.time, self.word)


class Vocabulary(models.Model):
    vocabulary = models.CharField(max_length=50, verbose_name="单词")
    chinese = models.CharField(max_length=50, verbose_name="中文释义")
    sentence = models.CharField(max_length=100, verbose_name="例句")
    chinese_sentence = models.CharField(max_length=100, verbose_name="例句翻译")

    type = models.CharField(max_length=100, verbose_name="被哪些单词书包含")

    # 通过子字符串匹配判断该单词被包含在哪些单词书中，

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['vocabulary'], name='vocabulary'),
        ]

    def __str__(self):
        return self.vocabulary
