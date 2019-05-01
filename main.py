# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import urlparse
import ConfigParser

import requests
from bs4 import BeautifulSoup
from xbmcswift2 import Plugin, xbmc


plugin = Plugin()
session = requests.Session()
session.headers.update(
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 \
            Safari/537.36'})

addon_dir = xbmc.translatePath('special://home/addons/{}'.format(plugin.id))
resource_conf = ConfigParser.ConfigParser()
resource_conf.read(os.path.join(addon_dir, 'conf', 'resource.ini'))


@plugin.route('/')
def index():
    items = list()
    plugin.log.info(resource_conf.sections())
    for area_name in resource_conf.options('ParentArea'):
        items.append({
            'label': area_name,
            'path': plugin.url_for('sub_categories', parent_id=resource_conf.get('ParentArea', area_name))
        })
    return items


@plugin.route('/live/category/<parent_id>')
def sub_categories(parent_id):
    items = list()
    url = 'https://live.bilibili.com/p/eden/area-tags?parentAreaId={}&areaId=0'.format(parent_id)
    resp = session.get(url)
    soup = BeautifulSoup(resp.content)
    html_as = soup.find('header', class_='header').section.find_all('a')
    for html_a in html_as:
        params = urlparse.parse_qs(urlparse.urlsplit(url).query)
        items.append({
            'label': html_a.text,
            'path': plugin.url_for('lives', parent_id=parent_id, area_id=params['areaId'][0], page=1)
        })
    for html_li in soup.find_all('li'):
        cover_style = html_li.div.a.find('div', class_='cover')['style']
        items.append({
            'label': html_li.div.a.find('div', class_='info').text,
            'thumbnail': cover_style[cover_style.index('(')+1:cover_style.index(')')],
            'path': plugin.url_for('live_play', detail=json.dumps({
                'roomid': html_li.div.a['href'][1:],
                'title': html_li.div.a.find('div', class_='info').text,
            }))
        })
    return items


@plugin.route('/live/category/<parent_id>/<area_id>/<page>/')
def lives(parent_id, area_id, page):
    items = []
    if int(page) > 1:
        items.append({
            'label': '上一页',
            'path': plugin.url_for('lives', parent_id=parent_id, area_id=area_id, page=int(page)-1)
        })
        items.append({
            'label': '首页',
            'path': plugin.url_for('lives', parent_id=parent_id, area_id=area_id, page=1)
        })
        page_size = 41
    else:
        page_size = 43

    url = 'https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web\
&parent_area_id={}&cate_id=0&area_id={}&sort_type=income&page={}\
&page_size={}&tag_version=1'.format(parent_id, area_id, page, page_size)
    resp = requests.get(url)
    data = resp.json()

    items.extend([{
        'label': detail['title'],
        'path': plugin.url_for('live_play', detail=json.dumps(detail)),
        'thumbnail': detail['user_cover'],
        'icon': detail['user_cover'],
    } for detail in data['data']['list']])
    items.append({
        'label': '下一页',
        'path': plugin.url_for('lives', parent_id=parent_id, area_id=area_id, page=int(page)+1)
    })
    return items


@plugin.route('/live/category/detail/<detail>/')
def live_play(detail):
    detail = json.loads(detail)
    resp = session.get('https://live.bilibili.com/{}'.format(detail['roomid']))
    plugin.log.info(resp.content)
    soup = BeautifulSoup(resp.text)
    room_info = json.loads(soup.find_all(
        'div', class_='script-requirement')[0].script.text[31:])
    play_infos = room_info['playUrlRes']['data']['durl']
    return plugin.finish([{
        'path': info['url'],
        'is_playable': True,
        'label': detail['title'],
    } for info in play_infos])


if __name__ == "__main__":
    plugin.run()
    plugin.set_view_mode(500)
