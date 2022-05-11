import requests
from bs4 import BeautifulSoup as BS

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:47.0) Gecko/20100101 Firefox/47.0',
           'Accept': 'text/html, application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
           }


def rabota(url, city=None, language=None):
    jobs = []
    errors = []

    if url:
        response = requests.get(url, headers=headers)
        soup = BS(response.content, 'html.parser')
        try:
            page = soup.find_all('span', class_='pager-item-not-in-short-range')[-1].get_text()
        except IndexError:
            page = 1
        for x in range(int(page)):
            response = requests.get(url + str(x), headers=headers)
            if response.status_code == 200:
                soup = BS(response.content, 'html.parser')
                main_div = soup.find('div', id='a11y-main-content')
                if main_div:
                    div_lst = main_div.find_all('div', attrs={'class': 'vacancy-serp-item'})
                    for div in div_lst:
                        title = div.find('div', attrs={'class': 'vacancy-serp-item__layout'})
                        job_title = title.a.text
                        href = title.a['href']
                        description = div.find('div', attrs={'class': 'g-user-content'})
                        responsibility = description.find('div',
                                                          attrs={
                                                              'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}
                                                          )
                        if responsibility:
                            responsibility = responsibility.text
                        else:
                            responsibility = ''
                        requirement = description.find('div', attrs={'class': 'bloko-text_no-top-indent'}).text
                        company = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
                        jobs.append(
                            {'title': job_title, 'url': href, 'description': str(responsibility) + requirement,
                             'company': company, 'city_id': city, 'language_id': language})
                else:
                    errors.append({'url': url, 'title': "Div does not exists"})
            else:
                errors.append({'url': url, 'title': "Page don't response"})
        return jobs, errors
