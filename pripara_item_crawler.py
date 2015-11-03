#! /usr/bin/env python
# coding: utf-8
# vim: ft=python fenc=utf-8 ts=4 sw=4

import lxml
import lxml.html
import os
import urllib2


class Item:

    __base_url = "http://pripara.jp/item/"

    def __init__(self, dom):
        _details = self.__getItemDetails(dom)
        self.image = _details['image']
        self.name = _details['name']
        self.id = _details['id']
        self.category = _details['category']
        self.type = _details['type']
        self.brand = _details['brand']
        self.rarity = _details['rarity']
        self.like = _details['like']
        self.color = _details['color']

    def __getItemDetails(self, dom):
        details = {}
        # image url
        details['image'] = dom.find('p').find('img').attrib['src']
        # id
        id = dom.find('div').find('h2').find('span').text
        if isinstance(id, type(None)):
            details['id'] = ''
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
            details['brand'] = brand.find('img').attrib['src']
        else:
            details['brand'] = ''
        # rarity
        details['rarity'] = table_lower.findall('td')[0].text
        # like
        details['like'] = table_lower.findall('td')[1].text
        # color
        details['color'] = table_lower.findall('td')[2].text

        return details


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

for item_url in item_urls:
    items = fetch_items(item_url)

    for dom in items:
        item = Item(dom)
        print item.name
