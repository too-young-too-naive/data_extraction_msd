# -*- coding: utf-8 -*-
from scrapy import Selector
import json
import codecs
import sys
import io
from config import *

reload(sys)


def extract_tree(file_name):
    with codecs.open(file_name, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        tree = data['content']
    return tree


def extract_url(file_name):
    with codecs.open(file_name, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        url = data['url']
    return url


def get_element(path, tree):
    sel = Selector(text=tree)
    xp = lambda x: sel.xpath(x).extract()
    return xp(path)


def get_title(tree):
    try:
        elements = get_element('//div/hgroup/h1/b/text()', tree)
        if len(elements) == 1:
            return elements[0]
        elif len(elements) == 0:
            return ''
        else:
            return elements[0]
    except Exception as E:
        print 'Error: ' + E
        return ''


def get_content(tree):
    try:
        elements = get_element('string(//div/section[@class="body headers topic-content"])', tree)
        if len(elements) > 0:
            return cleanup(elements[0])
    except Exception as E:
        print 'Error: ' + E
        return ''


def cleanup(text):
    if text is None:
        return ''
    text_new = text.strip().replace('\t', '').replace('\r', '').replace(' ', '').replace('\n\n', '')
    print text_new
    return text_new


def concat_to_json(tree, file_name):
    dic = dict()
    dic['url'] = extract_url(file_name)
    dic['title'] = get_title(tree)
    dic['content'] = get_content(tree)
    file_path = dic['title'] + '.json'
    with io.open(file_path, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(dic, ensure_ascii=False))


if __name__ == '__main__':
    tree = extract_tree('web5.json')
    title = get_title(tree)
    content = get_content(tree)
    concat_to_json(tree, 'web5.json')
