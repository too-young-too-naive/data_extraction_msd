# -*- coding: utf-8 -*-
from scrapy import Selector
import json
import codecs
import sys
import io
import re
from collections import OrderedDict

reload(sys)
# TITLE_xpath = ''
# AUTHOR_xpath = ''
# CONTENT_xpath = ''
# ABSTRACT_xpath = ''
# SECTION_xpath = ''
# HEAD_xpath = ''
# SUBTRACTION_xpath = ''
# SUBSECTION_xpath = ''
# SUBHEAD = ''
# SUBCONTENT = ''


# def get_condig(file_name):
#     with open(file_name) as f:
#         config = json.load(f)
#     return


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
        elements = get_element('string(//div/hgroup/h1)', tree)
        if len(elements) == 1:
            return cleanup(elements[0]).replace('\n', '')
        elif len(elements) == 0:
            return ''
        else:
            return elements[0].encode('utf-8')
    except Exception as e:
        print 'get_title() Error: ' + str(e)
        return ''


def get_author(tree):
    try:
        elements = get_element('string(//div/hgroup/p)', tree)
        if len(elements) == 1:
            return cleanup(elements[0])
        elif len(elements) == 0:
            return ''
        else:
            return elements[0].encode('utf-8')
    except Exception as e:
        print 'get_title() Error: ' + str(e)
        return ''


def get_content(tree):
    try:
        elements = get_element('//div/section[@class="body headers topic-content"]', tree)
        if len(elements) > 0:
            return elements[0]
    except Exception as e:
        print 'get_content() Error: ' + str(e)
        return ''


def get_content_str(tree):
    try:
        elements = get_element('string(//div/section[@class="body headers topic-content"])', tree)
        if len(elements) > 0:
            return cleanup(elements[0])
    except Exception as e:
        print 'Error: ' + str(e)
        return ''


# def get_abstract(content):
#     try:
#         elements = get_element('//div/p', content)
#         print len(elements)
#         for i in elements:
#             j = get_abstract('string(//*)', i)
#             print j
#         return ''
#         # for para in elements:
#         #     text = text + para + '\n'
#         # return [text]
#     except Exception as e:
#         print 'get_abstract() Error! ' + str(e)
#         return []


def get_section(content):
    try:
        elements = get_element('//div[@class="headers topic-content"]/section[@class="header  FHead" or @class="header  EHead"]', content)
        return elements
    except Exception as e:
        print 'get_section() Error! ' + str(e)
        return []


def get_head(section):
    try:
        head = get_element('string(//header/h2)', section)
        return cleanup(head[0])
    except Exception as e:
        print 'get_head() Error! ' + str(e)
        return ''


def get_summary(tree):
    try:
        summary = get_element('//section[@class="body headers topic-content"]/div[@class="para" or @class="list"]', tree)
        if len(summary) != 0:
            text = ''
            for x in summary:
                text += get_element('string(//*)', x)[0]
            text = cleanup(text)
            return text
        else:
            return ''
    except Exception as e:
        print 'get_summary() Error! ' + str(e)
        return ''

# def get_subabstract(section):
#     try:
#         subsection_tree = get_element('//section[@class="header GHead"]', section)
#         if len(subsection_tree) == 0:
#             elements = get_element('string(//*)', section)
#             # print elements
#             return elements
#         else:
#             return ''
#     except Exception as e:
#         print 'get_subabstract() Error! ' + str(e)
#         return ''


def get_subsection(section):
    if section == []:
        return ''
    try:
        subsection_head = get_element('//header/h3/span', section)
        subsection_summary = get_element('//div[@class="header-body"]/div[@class="para" or @class="list"]', section)
        subsection_tree = get_element('//section[@class="header GHead"]', section)
        dic = OrderedDict()
        if len(subsection_tree) == 0:
            substr = ''
            subsection_content = get_element('//div[@class="header-body"]/div[not(@class="photo")]', section)
            for x in subsection_content:
                substr += get_element('string(//*)', x)[0]
            substr = cleanup(substr)
            return substr
        if len(subsection_summary) != 0:
            # print len(subsection_summary)
            sub_summary = ''
            for x in subsection_summary:
                sub_summary += get_element('string(//*)', x)[0]
            dic['sub_summary'] = cleanup(sub_summary)
        for (i, j) in zip(subsection_head, subsection_tree):
            head = get_element('string(//*)', i)
            text = get_element('string(//*)', j)
            dic[head[0]] = cleanup_v2(head[0], cleanup(text[0]))
        return dic
    except Exception as e:
        print 'get_subsection() Error! ' + str(e)
        return ''


def without_sec_get_subsec(section):
    if section == []:
        return ''
    try:
        subsection_head = get_element('//header/h2', section)
        subsection_tree = get_element('//section[@class="header  GHead"]', section)
        if len(subsection_tree) == 0:
            substr = ''
            # subsection_content = get_element('string(//*)', section)
            # substr = cleanup(subsection_content[0])
            subsection_content = get_element('//div[@class="header-body"]/div[not(@class="photo")]', section)
            for x in subsection_content:
                substr += get_element('string(//*)', x)[0]
            substr = cleanup(substr)
            return substr
        dic = OrderedDict()
        for (i, j) in zip(subsection_head, subsection_tree):
            head = get_element('string(//*)', i)
            text = get_element('string(//*)', j)
            dic[head[0]] = cleanup_v2(head[0], cleanup(text[0]))
        return dic
    except Exception as e:
        print 'get_subsection() Error! ' + str(e)
        return ''

def cleanup(text):
    if text is None:
        return ''
    tmp0 = re.sub(' +', ' ', text)
    tmp1 = tmp0.strip().replace('\t', '').replace('\r', '')
    tmp2 = re.sub('\n +', '\n', tmp1)
    tmp3 = re.sub('\n+', '\n', tmp2)
    return tmp3


def cleanup_v2(aim, text):
    regex = '^' + aim + '\n'
    res = re.sub(regex, '', text)
    return res


def concat_to_json(tree, file_name):
    file_path = 'data_' + file_name
    # file_path = 'extracted_data/data_' + file_name.split('/')[1]
    dic0 = OrderedDict()
    dic0['url'] = extract_url(file_name)
    dic0['title'] = get_title(tree)
    dic0['author'] = get_author(tree)
    dic0['summary'] = get_summary(tree)
    dic0['content_str'] = get_content_str(tree)
    if dic0['content_str'] == '':
        print file_name + 'has no useful information.'
        return
    content = get_content(tree)
    dic1 = OrderedDict()
    section = get_section(content)
    if len(section) == 0:
        dic2 = without_sec_get_subsec(tree)
        dic0['content'] = dic2
    else:
        for sec in section:
            head = get_head(sec)
            subsec = get_subsection(sec)
            # print str(type(subsec))
            if type(subsec) is unicode:
                subsec = cleanup_v2(head, subsec)
            dic1[head] = subsec
        dic0['content'] = dic1
    with io.open(file_path, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(dic0, ensure_ascii=False))


def filter():
    # for i in range(12000):
    #     try:
    #         file_zh = 'web' + str(i) + '.json'
    #         concat_to_json(extract_tree('json_file/' + file_zh), 'json_file/' + file_zh)
    #         print file_zh
    #         file_en = 'web' + str(i) + '_en.json'
    #         concat_to_json(extract_tree('json_file/' + file_en), 'json_file/' + file_en)
    #         print file_en
    #     except Exception as e:
    #         print 'Error: ' + str(e)
    try:
        # file_zh = 'web' + str(i) + '.json'
        # concat_to_json(extract_tree(file_zh), 'json_file/' + file_zh)
        # print file_zh
        file_en = 'web99.json'
        concat_to_json(extract_tree(file_en), file_en)
        print file_en
    except Exception as e:
        print 'Error: ' + str(e)

if __name__ == '__main__':
    filter()
