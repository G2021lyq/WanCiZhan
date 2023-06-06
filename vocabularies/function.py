import urllib.request
import urllib.parse
import json

import nltk
from nltk.corpus import wordnet

import matplotlib.pyplot as plt
import matplotlib as mpl

'''
# download needed nltk data files (if not downloaded already)
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
'''

def get_word_definition(word):
    synonyms = []
    antonyms = []

    # get word definitions
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
            if lemma.antonyms():
                antonyms.append(lemma.antonyms()[0].name())

    # remove duplicates and return the list of synonyms
    synonyms = list(set(synonyms))
    antonyms = list(set(antonyms))
    return synonyms, antonyms


def get_related_words(word):
    # get the word's part of speech
    tagged_word = nltk.pos_tag([word])[0]
    pos = tagged_word[1]

    # get the relevant synsets based on the word's part of speech
    if pos.startswith('JJ'):
        # adjective
        synsets = wordnet.synsets(word, pos=wordnet.ADJ)
    elif pos.startswith('RB'):
        # adverb
        synsets = wordnet.synsets(word, pos=wordnet.ADV)
    elif pos.startswith('VB'):
        # verb
        synsets = wordnet.synsets(word, pos=wordnet.VERB)
    elif pos.startswith('NN'):
        # noun
        synsets = wordnet.synsets(word, pos=wordnet.NOUN)
    else:
        synsets = []

    # get synonyms and antonyms from the relevant synsets
    synonyms, antonyms = [], []
    for synset in synsets:
        for lemma in synset.lemmas():
            word = lemma.name().replace('_', ' ')
            synonyms.append(word)
            if lemma.antonyms():
                antonyms.append(lemma.antonyms()[0].name().replace('_', ' '))

    # remove duplicates and return the list of synonyms
    synonyms = list(set(synonyms))
    antonyms = list(set(antonyms))
    return synonyms, antonyms


def associate(word):
    synonyms, antonyms = get_word_definition(word)
    related_words, _ = get_related_words(word)
    return synonyms, antonyms, related_words

'''
if __name__ == '__main__':
    word = "mother"
    print(associate(word))
'''

# 存在问题，然后的内容不仅仅是单词的释义，而且还有其他的引申
def TranslateWord(word):
    # 百度翻译的API接口
    url = "https://fanyi.baidu.com/sug"
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    # 要加的参数
    data = {
        'kw': word,
    }
    data = urllib.parse.urlencode(data).encode()
    request = urllib.request.Request(url=url, headers=headers, data=data)
    response = urllib.request.urlopen(request).read().decode('unicode_escape')
    # 用Json模块把得到的json数据（其实它就是一种str字符串）转成Python中字典
    response = json.loads(response)['data']
    string = ""
    for word in response:
        string = string + word['k'] + '：' + word['v'] + '\n'
    return string

'''
if __name__ == '__main__':
    word = 'name'
    string = TranslateWord(word)
    print(string)
'''


import random
import string

def random_string(length=6):
    """生成指定长度的随机字符串"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(length))

def make_picture(scores):
    print(scores)
    mpl.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体支持
    fig = plt.figure()  # 生成一个空白图形并且将其赋值给fig对象
    # 假设测试记录如下

    # 绘制得分折线图S
    plt.plot(range(1, len(scores) + 1), scores)
    plt.xlabel('测试次数')
    plt.ylabel('得分')
    plt.title('单词测试情况')
    plt.xticks(range(1, len(scores) + 1))
    plt.yticks(range(0, 11))
    plt.grid(True)
    # fig.savefig("first.png", transparent=True)
    rand_string = random_string()
    save_url = "vocabularies/static/img/" + rand_string + ".png"
    print(save_url)
    fig.savefig(save_url)
    save_url = "/static/img/" + rand_string + ".png"
    return save_url
