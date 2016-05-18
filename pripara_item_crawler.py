#! /usr/bin/env python
# coding: utf-8
# vim: ft=python fenc=utf-8 ts=4 sw=4

import lxml
import lxml.html
import json,codecs
import unicodedata
import urllib2
import hashlib
from boto.s3.connection import S3Connection
from boto.s3.key import Key


class Item:

    __base_url = "http://pripara.jp/item/"

    def __init__(self, dom):
        _details = self.__getItemDetails(dom)
        for key in _details:
            _details[key] = unicodedata.normalize('NFKC', unicode(_details[key]))

        self.image = self.__convertS3(_details['image'])
        self.name = _details['name']
        self.id = _details['id']
        self.category = _details['category']
        self.type = _details['type']
        self.brand = _details['brand']
        self.rarity = _details['rarity'] if _details['rarity'] != ' ' else 'nullrarity'
        _details['like'] = '0' if _details['like'] == '?' else _details['like']
        try:
            self.like = _details['like'] if int(_details['like']) != ' ' else 0
        except ValueError:
            self.like = 0

        self.color = _details['color'] if _details['color'] != ' ' else 'nullcolor'

    def to_dict(self):
        d = {
            'image': self.image,
            'name': self.name,
            'id': self.id,
            'category': self.category,
            'type': self.type,
            'brand': self.brand,
            'rarity': self.rarity,
            'like': self.like,
            'color': self.color,
        }
        return d

    def __getItemDetails(self, dom):
        details = {}
        # image url
        details['image'] = self.__base_url + dom.find('p').find('img').attrib['src']
        # id
        id = dom.find('div').find('h2').find('span').text
        if isinstance(id, type(None)):
            details['id'] = 'nullid'
        else:
            details['id'] = id
        # name
        details['name'] = dom.find('div').find(
            'h2').text_content().replace(details['id'], '')

        table_upper = dom.find('table').findall('tr')[1]
        table_lower = dom.find('table').findall('tr')[3]
        # category
        details['category'] = table_upper.findall('td')[0].text
        # type
        details['type'] = table_upper.findall('td')[1].text
        # brand
        brand = table_upper.findall('td')[2]
        if isinstance(brand.text, type(None)):
            details['brand'] = brand.find('img').attrib['alt']
        else:
            details['brand'] = 'nullbrand'
        # rarity
        details['rarity'] = table_lower.findall('td')[0].text
        # like
        details['like'] = table_lower.findall('td')[1].text
        # color
        details['color'] = table_lower.findall('td')[2].text

        return details

    def __generate_hash(self,url):
        return hashlib.md5(url).hexdigest()

    def __convertS3(self, image_url):
        aws_access_key_id = 'AKIAIXDB6A77I3CMBY6Q'
        aws_secret_access_key = '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'
        
        conn = S3Connection( aws_access_key_id, aws_secret_access_key)
        bucket = conn.get_bucket('pripara')
        
        f = Key(bucket)
        f.key = self.__generate_hash(image_url) + '.jpg'
        f.set_contents_from_string(urllib2.urlopen(image_url).read())
        f.make_public()

        return f.generate_url(expires_in=0, query_auth=False)


def fetch_item_urls(item_url):
    req = urllib2.Request(item_url)
    html = urllib2.urlopen(req).read()
    root = lxml.html.fromstring(html)

    item_urls = root.xpath(
        '//*[@id="contentBodyMain"]/div/div[1]/div/ul/li/a')

    item_sub_urls = [item.attrib['href'] for item in item_urls]

    return item_sub_urls


def fetch_items(url):
    req = urllib2.Request(item_url)
    html = urllib2.urlopen(req).read()
    root = lxml.html.fromstring(html)

    items = root.xpath(
        '//*[@id="contentBodyMain"]/div/div[2]/div[3]/div')

    return items



base_url = 'http://pripara.jp/item/'
item_url = 'http://pripara.jp/item/dream201511_4th.html'
item_sub_urls = fetch_item_urls(item_url)
item_urls = [base_url + item_sub_url for item_sub_url in item_sub_urls]

pripara_items = {}

for item_url in item_urls:
    season = item_url.replace(base_url, '')[:-5]
    items = fetch_items(item_url)
    print season
    for dom in items:
        item = Item(dom)
        d = { unicode(item.id) : item.to_dict()}
        pripara_items.setdefault(season,[]).append(d)

f=codecs.open('pripara_code.json', 'w', 'utf-8')
json.dump(pripara_items, f, indent=2,ensure_ascii=False)
f.close()
