import os
import json
import codecs


def extract_url(file_name):
    with codecs.open(file_name, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        url = data['url']
    return url


def delete_file():
    for i in range(12000):
        file_path = 'json_file/web' + str(i) + '.json'
        try:
            url = extract_url(file_path)
            if url.split('/')[3] != 'zh':
                os.remove(file_path)
        except Exception as e:
            print 'Error: ' + str(e)


def delete_file_v2():
    file_path = 'web0.json'
    try:
        url = extract_url(file_path)
        if url.split('/')[3] != 'zh':
                os.remove(file_path)
                print file_path + ' deleted success!'
        else:
            print file_path + ' is zh-CN'
    except Exception as e:
        print 'Error: ' + str(e)

if __name__ == '__main__':
    delete_file_v2()