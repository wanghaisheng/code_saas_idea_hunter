import arxivscraper
import datetime
import time
import requests
import json
from datetime import timedelta
import os

def get_daily_code(DateToday,cats,filters):
    """
    @param DateToday: str
    @param cats: dict
    @return paper_with_code: dict
    """
    from_day = until_day = DateToday
    content = dict()
    # content
    output = dict()
    for k,v in cats.items():
        scraper = arxivscraper.Scraper(category=k, date_from=from_day,date_until=until_day,filters=filters)
        tmp = scraper.scrape()
        print(tmp)
        if isinstance(tmp,list):
            for item in tmp:
                if item["id"] not in output:
                    output[item["id"]] = item
        time.sleep(30)

    base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"
    cnt = 0

    for k,v in output.items():
        print(v["id"])
        _id = v["id"]
        paper_title = " ".join(v["title"].split())
        paper_url = v["url"]
        url = base_url + _id
        try:
            r = requests.get(url).json()
            if "official" in r and r["official"]:
                cnt += 1
                repo_url = r["official"]["url"]
                repo_name = repo_url.split("/")[-1]

                content[_id] = f"|[{paper_title}]({paper_url})|[{repo_name}]({repo_url})|\n"
        except Exception as e:
            print(f"exception: {e} with id: {_id}")
    data = {DateToday:content}
    return data

def update_daily_json(filename,data_all):
    if not os.path.exists(filename):
        open(filename,'w').write('')
    with open(filename,"r") as f:
        content = f.read()
        if not content:
            m = {}
        else:
            m = json.loads(content)
    
    #将datas更新到m中
    for data in data_all:
        m.update(data)

    # save data to daily.json

    with open(filename,"w") as f:
        json.dump(m,f)
    



def json_to_md(jsonfilename,mdfilename):
    """
    @param filename: str
    @return None
    """

    with open(jsonfilename,"r") as f:
        content = f.read()
        if not content:
            data = {}
        else:
            data = json.loads(content)
    # clean README.md if daily already exist else creat it
    with open("web/README{}.md".format(mdfilename.split('.')[0]),"w+") as f:
        pass
    # write data into README.md
    with open("web/README{}.md".format(mdfilename.split('.')[0]),"a+") as f:
        # 对data数据排序
        for day in sorted(data.keys(),reverse=True):
            day_content = data[day]
            if not day_content:
                continue
            # the head of each part
            f.write(f"## {day}\n")
            f.write("|paper|code|\n" + "|---|---|\n")
            for k,v in day_content.items():
                f.write(v)
    
    print("finished")        
cats={
"ComputerScience":["cs"],
# "Economics":["econ"],
"ElectricalEngineeringandSystemsScience":["eess"],
# "Mathematics":["math"],
# "Physics":["physics"],
# "Astrophysics":["physics:astro-ph"],
# "CondensedMatter":["physics:cond-mat"],
# "GeneralRelativityandQuantumCosmology":["physics:gr-qc"],
# "HighEnergyPhysics-Experiment":["physics:hep-ex"],
# "HighEnergyPhysics-Lattice":["physics:hep-lat"],
# "HighEnergyPhysics-Phenomenology":["physics:hep-ph"],
# "HighEnergyPhysics-Theory":["physics:hep-th"],
# "MathematicalPhysics":["physics:math-ph"],
# "NonlinearSciences":["physics:nlin"],
# "NuclearExperiment":["physics:nucl-ex"],
# "NuclearTheory":["physics:nucl-th"],
# "Physics(Other)":["physics:physics"],
# "QuantumPhysics":["physics:quant-ph"],
# "QuantitativeBiology":["q-bio"],
# "QuantitativeFinance":["q-fin"],
# "Statistics":["stat"]
}
if __name__ == "__main__":

    DateToday = datetime.date.today()
    N = 7 # 往前查询的天数
    data_all = []
    for i in range(1,N):
        day = str(DateToday + timedelta(-i))
        # you can add the categories in cats

        healthcare_papar_code={'categories':['cs', 'eess'],'abstract':['healthcare','medical','hospital']}
        data = get_daily_code(day,cats,healthcare_papar_code)
        data_all.append(data)
    update_daily_json("data/{}.json".format('healthcare_papar_code'),data_all)
    json_to_md("data/{}.json".format('healthcare_papar_code'),'-healthcare_papar_code')
