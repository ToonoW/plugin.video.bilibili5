# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import requests
from requests_html import HTMLSession
from xbmcswift2 import Plugin


plugin = Plugin()


@plugin.route('/')
def index():
    items = [{
        'label': '直播',
        'path': plugin.url_for('/category/live', page=1)
    }]
    return items


@plugin.route('/category/live')
def live(page):
    url = 'https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=1&cate_id=0&area_id=33&sort_type=income&page=1&page_size=60&tag_version=1'
    resp = requests.get(url)
    data = resp.json()
    return [{
        'label': detail['title'],
        'path': plugin.url_for('/category/live', room_id=detail['roomid']),
        'thumbnail': detail['user_cover'],
        'icon': detail['user_cover'],
        'is_playable': True,
    } for detail in data['data']['list']]


@plugin.route('/category/live/<room_id>')
def live_play(room_id):
    session = HTMLSession()
    resp = session.get('https://live.bilibili.com/{}'.format(room_id))
    room_info = json.loads(resp.html.xpath(
        '//div[@class="script-requirement"]/script[1]/text()')[0][31:])
    play_urls = room_info['playUrlRes']['data']['durl']
    plugin.set_resolved_url(play_urls[0]['url'])


if __name__ == "__main__":
    plugin.run()
    plugin.set_view_mode(500)
