import lxml.html
import requests
import re
import os
from multiprocessing.dummy import Pool
import time
import multiprocessing as ms

url_novel = 'https://www.kanunu8.com/book2/10888/index.html'

def get_source(url:str) -> str:
    html = requests.get(url)
    return html.content.decode(encoding='gbk')

def get_article_info(html:str):
    selector = lxml.html.fromstring(html)
    info_list = selector.xpath('/html/body/div[2]/div[2]/div/table[2]/tbody/tr')
    
    chapter_value = []
    part_name = ''
    result_list = []
    for info in info_list:
        _part_name = info.xpath('./td/strong/text()')
        if len(_part_name) > 0:
            if len(chapter_value) > 0:
                result_list.append({'part_key':part_name[:],'part_value':chapter_value.copy()})
                chapter_value.clear()
            part_name = _part_name[0]

        chapter_name_list = info.xpath('./td/a/text()')
        chapter_url_list = info.xpath('./td/a/@href')

        for i in range(len(chapter_name_list)):
            result_chapter ={} 
            result_chapter['chapter'] = chapter_name_list[i]
            result_chapter['url'] = url_novel.replace('index.html',chapter_url_list[i])
            chapter_value.append(result_chapter)

        if info == list(info_list)[-1]:
            result_list.append({'part_key':part_name[:],'part_value':chapter_value.copy()})
            chapter_value.clear()
    return result_list

def get_article(content:str)->str:
    article = re.findall('<p>(.*?)</p>',content,re.S)
    if len(article) == 0:
        return None
    article_content = article[0].replace('&nbsp;',' ').replace('<br />','').replace('\n\n','')
    return article_content


def save(path:str,name:str,article:str):
    os.makedirs(path,exist_ok=True)
    with open(os.path.join(path,name+'.txt'),'w',encoding='utf-8') as f:
            f.write(article)
            
def query_article(path:str,name,url:str):
    toc_html = get_source(url)
    toc_text = get_article(toc_html)
    if toc_text is None:
        return
    save(path,name,toc_text)

def run():
    main_dir = 'novel1'
    toc_list = []
    pool = Pool(20)
    toc_html = get_source(url_novel)
    result_list = get_article_info(toc_html)
    for info in result_list:
        part_key,part_value=info.values()
        for chapter_info in part_value:
            chapter,url = chapter_info.values()
            toc_list.append([main_dir+'/'+part_key,chapter,url])
    pool.starmap(query_article,toc_list)

start = time.time()
run()
end = time.time()
print(f'多线程耗时：{end - start}')

print(f'最大线程数：{ ms.cpu_count()}')