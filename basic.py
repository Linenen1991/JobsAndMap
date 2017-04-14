import re
import json
from urllib.request import urlopen
from urllib.error import HTTPError
import googlemaps
from bs4 import BeautifulSoup


def parse_html(www):
    "open the url ,and trans into BeautifulSoup Obj"
    try:
        html = urlopen(www)
        return BeautifulSoup(html.read(), "html.parser")
    except HTTPError as e:
        print(e.code)
        return None


def get_number(page):
    "search for page number in BeautifulSoup obj"
    try:
        target = page.find(text=re.compile("共 \d+ 頁"))
    except AttributeError as e:
        print("missing information about page")
        return None
    return re.search("共 (\d+) 頁", target).group(1)


def find_LatLng(address, API_key):
    "return lat,lng of address. "
    gmaps = googlemaps.Client(key=API_key)
    geocode_result = gmaps.geocode(address)
    # if the result is null,it will try address with removing the content in brace
    if geocode_result == []:
        remove_brace = re.sub(r"\(.+\)", "", address)
        geocode_result = gmaps.geocode(remove_brace)
        if geocode_result == []:
            return None
    return geocode_result[0]['geometry']['location']


def get_job_address(job_page):
    "search the location of the job in page"
    location = job_page.find(text=re.compile('var jlocation=\[.+\];'))
    text = re.search('var jlocation=\[(.+?),(.+?),\'(.+?)\'];', location, re.M)
    lat = float(text.group(1))
    lng = float(text.group(2))
    address = text.group(3)
    return [lat, lng, address]


def find_jobs(page):
    "list all job in the page"
    job_list = page.find_all("div", {"class": "j_cont line_bottom"})
    jobs = []
    for job in job_list:
        job_info = job.find("ul", {"class": "summary_tit"}).find(
            "div", {"class": "jobname_summary job_name"})
        full_url = "https://www.104.com.tw" + job_info.a['href']
        jobs.append([job_info.get_text(), full_url])
    return jobs


def find_jobs_freshman(page):
    "list all job in the page (only for 新鮮人找工作)"
    lists = page.find_all("div", {"class": "joblist_cont"})
    jobs = []
    for tag in lists:
        job_info = tag.find("div", {"class": "jobname"}).find(
            "a", {"target": "_blank"})
        url = "https://www.104.com.tw" + job_info['href']
        name = re.sub('[\r\n\t]', '', job_info.get_text())
        jobs.append([name, url])
    return jobs


def collecting(location_job, url_job, data):
    "collecting job into data"
    found = 0
    for o in data:
        if o['location'] == location_job:
            if isinstance(url_job, list):
                o['urls'] = url_job + o['urls']
            else:
                o['urls'].append(url_job)
            found = 1
            break
    if found == 0:
        if isinstance(url_job, list):
            data.append({"location": location_job, "urls": url_job})
        else:
            data.append({"location": location_job, "urls": [url_job]})

def dump_to_file(dic, file_name, be_var=None):
    "save the dic to js file"
    with open(file_name, 'w') as outfile:
        outfile.flush()
        if be_var != None:
            outfile.write("var data =")
        json.dump(dic, outfile)
        outfile.close()
