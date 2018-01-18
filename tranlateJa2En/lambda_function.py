# coding: UTF-8
import boto3
import urllib.request
import logging
import xml.etree.ElementTree as ET
import urllib

#Region指定しないと、デフォルトのUSリージョンが使われる
client_lambda = boto3.client('lambda', region_name='ap-northeast-1')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info('Loading function')

def lambda_handler(event, context):

    # このサービスが動作するか決定する。英単語１つしか入ってないときに動かす
    line_text = event["lineMessage"]["events"][0]["message"]["text"]
    # print(line_text)
    
    first_content = event["analysedMessage"]["tokens"][0]["text"]["content"]
    language = event["analysedMessage"]["language"]
    
    logger.info("line_text=%s:first_content=%s:language=%s",line_text,first_content,language)
    
    print(event["analysedMessage"])
    if "翻訳して" in line_text and language == "ja":
        search_word = line_text.replace("翻訳して","")
    else:
        return None
    
    # 検索
    print(type(search_word))
    #item_id = get_item_id(u'りんご'.decode('utf-8'))
    item_id = get_item_id(search_word)
    translated_text = get_translated_text(item_id)

    logger.info("translated_text=%s",translated_text)

    #取得した翻訳結果を返す
    if translated_text is None:
        return None
    else:
        return { "message" : translated_text }

# 翻訳サービスが返すxmlから結果を抽出する
def get_xml_element_text(url, tag):
    print(url)
    try:
        xml = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print('error code : ' + str(e.code))
        print('error read : ' + str(e.read()))
        return ''
    tree = ET.parse(xml)
    
    print("xml:",xml.read())
    
    root = tree.getroot()
    element = root.find('.//{http://btonic.est.co.jp/NetDic/NetDicV09}' + tag)
    print("root: ",root)
    print("tree: ",tree)
    print("element: ",element)
    text = element.text
    return text

# 翻訳サービスからワードのIDを取得
def get_item_id(search_word):
    head = 'http://public.dejizo.jp/NetDicV09.asmx/SearchDicItemLite?Dic=EdictJE&Word='
    end = '&Scope=HEADWORD&Match=EXACT&Merge=OR&Prof=XHTML&PageSize=20&PageIndex=0'
    print(urllib.parse.quote(search_word))
    url = head + urllib.parse.quote(search_word) + end
    
    return get_xml_element_text(url, 'ItemID')

# 翻訳サービスにワードIDを投げて結果を取得
def get_translated_text(item_id):
    head = 'http://public.dejizo.jp/NetDicV09.asmx/GetDicItemLite?Dic=EdictJE&Item='
    end = '&Loc=&Prof=XHTML'
    url = head + item_id + end
    print(url)
    return get_xml_element_text(url, 'Body/div/div/div')