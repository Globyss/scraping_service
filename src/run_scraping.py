

from django.contrib.auth import get_user_model

from scraping.parsers import rabota
import os
import sys
import django
import datetime as dt

proj = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(proj)
os.environ['DJANGO_SETTINGS_MODULE'] = 'scraping_service.settings'
django.setup()

from django.db import DatabaseError
from scraping.models import Vacancy, Error, Url

User = get_user_model()

parsers = [(rabota, 'rabota')]


def get_settings():
    qs = User.objects.filter(send_email=True).values()
    settings_lst = set((q['city_id'], q['language_id']) for q in qs)
    return settings_lst


def get_urls(_settings):
    qs = Url.objects.all().values()
    url_dct = {(q['city_id'], q['language_id']): q['url_data'] for q in qs}
    urls = []
    for pair in _settings:
        if pair in url_dct:
            if pair[0] and pair[1] is not None:
                tmp = {'city': pair[0], 'language': pair[1], 'url_data': url_dct[pair]}
                urls.append(tmp)
    return urls


settings = get_settings()
url_list = get_urls(settings)

jobs, errors = [], []
for data in url_list:
    for func, key in parsers:
        url = data['url_data'][key]
        j, e = func(url, city=data['city'], language=data['language'])
        jobs += j
        errors += e

for job in jobs:
    v = Vacancy(**job)
    try:
        v.save()
    except DatabaseError:
        pass
if errors:
    qs = Error.objects.filter(timestamp=dt.date.today())
    if qs.exists():
        er = qs.first()
        er.data.update({'errors': errors})
        er.save()
    else:
        er = Error(data=f'errors:{errors}').save()
ten_days_ago = dt.date.today() - dt.timedelta(10)
Vacancy.objects.filter(timestamp__lte=ten_days_ago).delete()
  