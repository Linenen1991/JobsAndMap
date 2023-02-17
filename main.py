#!./venv/bin/python3
import time
import basic
import json
import re

dic = []
# base_url = "https://www.104.com.tw/jobbank/joblist/joblist.cfm?jobsource=n104bank1&ro=0&jobcat=2007001000%2C2007002000&area=6001014000&expcate=2&order=2&asc=0&page={0}"
base_url = "https://www.104.com.tw/area/freshman/job/softwareengineer?area=6001014000&jobcategory=2007001000%2C2007002000&industry=&keyword=&page={0}&sortField=APPEAR_DATE&sortMode=DESC"  # 新鮮人找工作
min_index = 3
APIkey = ""
ob_page = basic.parse_html(base_url)
min_index = min(int(basic.get_number(ob_page)), min_index)
for page_index in range(min_index, 0, -1):
    indexd_url = base_url.format(page_index)
    bs_page = basic.parse_html(indexd_url)
    jobs = basic.find_jobs_freshman(bs_page)
    for i in jobs:
        job_url = i[1]
        print(job_url)
        bs_job = basic.parse_html(job_url)
        location_info = basic.get_job_address(bs_job)
        print(location_info)
        if location_info is None:
            continue
        posittion = basic.find_LatLng(location_info[2], APIkey)
        print(posittion)
        if posittion is None:
            continue
        basic.collecting(posittion, job_url, dic)
        time.sleep(300)

print(dic)

basic.dump_to_file(dic, 'freshman.json')
