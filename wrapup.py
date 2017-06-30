import io
from urllib2 import urlopen
import json
import codecs
import string
import chardet
from scrapy import Selector
from urllib import quote_plus


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


def spider(url, file_path):
    try:
        response = urlopen(quote_plus(url.encode('utf-8'), safe=string.printable))
        # make sure get the html data
        if response.info().gettype() == 'text/html':
            html_bytes = response.read()
            decode_type = chardet.detect(html_bytes)['encoding']
            html_string = html_bytes.decode(decode_type)
            concat_json(html_string, url, file_path)
    except Exception as e:
        print 'Error: can not crawl page! : ' + str(e)


def concat_json(text, url, file_path):
    html_text = dict()
    html_text['url'] = url
    html_text['content'] = text
    enfile_name = file_path.split('.')[0] + '_en' + '.json'
    with io.open(enfile_name, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(html_text, ensure_ascii=False))


def crawl_en_page():
    for i in range(12000):
        file_path = 'web' + str(i) + '.json'
        try:
            tree = extract_tree(file_path)
            url = extract_url(file_path)
            if url.split('/')[3] == 'zh':
                en_url = get_element('/html/head/link[8]/@href', tree)
                print en_url[0]
                print type(en_url[0])
                spider(en_url[0], file_path)
        except Exception as e:
            print 'Error: no file as name ' + file_path + 'or'
            print str(e)


def crawl_en_page_v2():
        file_path = 'web4.json'
        try:
            tree = extract_tree(file_path)
            url = extract_url(file_path)
            if url.split('/')[3] == 'zh':
                en_url = get_element('/html/head/link[8]/@href', tree)
                print en_url[0]
                print type(en_url[0])
                spider(en_url[0], file_path)
        except Exception as e:
            print 'Error: no file as name ' + file_path + 'or'
            print str(e)

if __name__ == '__main__':
    crawl_en_page_v2()
