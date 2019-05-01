# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import requests
from bs4 import BeautifulSoup
from xbmcswift2 import Plugin


plugin = Plugin()
session = requests.Session()
session.headers.update(
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 \
            Safari/537.36'})


@plugin.route('/')
def index():
    items = [{
        'label': '直播',
        'path': plugin.url_for('live', page=1)
    }]
    return items


@plugin.route('/live/category/<page>/')
def live(page):
    items = []
    if int(page) > 1:
        items.append({
            'label': '上一页',
            'path': plugin.url_for('live', page=int(page)-1)
        })
        items.append({
            'label': '首页',
            'path': plugin.url_for('live', page=1)
        })
        page_size = 41
    else:
        page_size = 43

    url = 'https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web\
&parent_area_id=1&cate_id=0&area_id=33&sort_type=income&page={}\
&page_size={}&tag_version=1'.format(page, page_size)
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
        'path': plugin.url_for('live', page=int(page)+1)
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
