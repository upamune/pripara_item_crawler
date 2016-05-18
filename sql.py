from __future__ import unicode_literals
import json
import codecs

table_name = ''

def item_to_sql(item, seeason):
    image = item[u'image']
    name = item[u'name']
    id = item[u'id']
    category = item[u'category']
    type = item[u'type']
    brand = item[u'brand']
    rarity = item[u'rarity']
    likes = item[u'like']
    color = item[u'color']

    sql = 'INSERT INTO %s (code, name, imageURL, category, type, brand, rarity, likes, color, season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \n' % (table_name, id, name, image, category, type, brand, rarity, int(likes), color, season)

    return sql

f = codecs.open('./pripara_code.json', 'r', 'utf-8')
j = json.load(f)

for season in j:
    sqls = []
    for item in j[season]:
        for id in item:
            sql = item_to_sql(item[id], season)
            sqls.append(sql.encode('utf-8'))

    f = open(season + ".sql", "w")
    for sql in sqls:
        f.write(sql)
    f.close()
