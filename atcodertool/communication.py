import os, sys
import pickle
import requests
from bs4 import BeautifulSoup
from uroboros import ExitStatus
from urllib import parse
import toml, json
import getpass
import atcodertool.config as conf

ATCODER_ENDPOINT = "https://atcoder.jp/contests/"
COOKIE_FILE = os.path.expanduser(conf.read_config()["session"]["cookie_file_path"])
LOGIN_URL = "https://atcoder.jp/login"
INFO_DIR_PATH = ".atcoder_tool"

def new_session(config):
    session = requests.session()
    # csrf_token取得
    r = session.get(LOGIN_URL)
    s = BeautifulSoup(r.text, 'lxml')
    csrf_token = s.find(attrs={'name': 'csrf_token'}).get('value')
    
    # パラメータセット
    if config["session"]["username"] == "":
        user = input("atcoder username: ")
        config["session"]["username"] = user
        conf.config_update(config)
    else:
        user = config["session"]["username"]
    password = getpass.getpass("password: ")
    login_info = {
        "csrf_token": csrf_token,
        "username": user,
        "password": password,
    }

    result = session.post(LOGIN_URL, data=login_info)
    result.raise_for_status()
    if result.status_code==200:
        print("log in!")
    else:
        print("failed...")
        return ExitStatus.FAILURE
    
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(session.cookies, f)
    return session

def make_session(config):
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "rb") as f:
            c = pickle.load(f)
            session = requests.session()
            session.cookies.update(c)
    else:
        session = new_session(config)
    return session



def submit(codes, problem_id, contest_id, config):
    session = make_session(config)
    info = contest_info(contest_id, config)    
    tar = ATCODER_ENDPOINT + contest_id + "/submit"

    html = session.get(tar)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "lxml")
    csrf_token = soup.find(attrs={"name": "csrf_token"}).get("value")
    lang_id = -1
    for d in soup.find_all("option"):
        if config["language"]["lang"] in d.text:
            lang_id = d.get("value")
            break
    if lang_id == -1:
        print("lang:{lang} seems not be available in {contest}...".format(
            lang = config["language"]["lang"],
            contest = contest_id
        ))
        return ExitStatus.FAILURE

    submit_info = {
        "data.TaskScreenName": info[problem_id]["url"],
        "csrf_token": csrf_token,
        "data.LanguageId":  lang_id,  #int(config["language"]["lang_id"]),
        "sourceCode": codes
    }
    res = session.post(tar, data=submit_info)
    #res.raise_for_status()
    if res.status_code != 200:
        print("Failed to submit source codes.")
        print("HTTP status code is {res}".format(res=res))
        return ExitStatus.FAILURE
    return ExitStatus.SUCCESS

def contest_info(contest_id, config):
    info_file = os.path.join(INFO_DIR_PATH, "contest_info.json")
    if os.path.split(os.getcwd())[1] != contest_id:
        info_file = os.path.join(contest_id, info_file)

    if os.path.exists(info_file):
        with open(info_file, "r") as f:
            info = json.load(f)
        return info
    session = make_session(config)
    page = session.get(ATCODER_ENDPOINT + contest_id + "/tasks")
    table = BeautifulSoup(page.text, "lxml").find("tbody")
    if table == None:
        return []
    table = table.find_all("td")
    num = len(table) / 5
    num = int(num)
    problems = {}
    for i in range(num):
        problem = {}
        pid = table[i*5].text.lower()
        url = table[i*5+1].a.get("href")
        problem["url"] = os.path.split(parse.urlparse(url).path)[1]
        problem["tle"] = int(table[i*5+2].text[:-3])
        problem["mle"] = int(table[i*5+3].text[:-2])
        problems[pid] = problem
    with open(info_file, "x") as f:
        json.dump(problems, f, indent=4)
    return problems

def scrape_page(problem_id, contest_id, config):
    info = contest_info(contest_id, config)
    session = make_session(config)
    page = session.get(ATCODER_ENDPOINT + contest_id + 
        "/tasks/" + info[problem_id]["url"])
    testcase = choose_cases(page)
    return testcase

def choose_cases(page_org):
    """取得した問題のページから問題部分を抽出する"""

    page = BeautifulSoup(page_org.text, 'lxml').find_all(class_ = "part")
    res = []
    case = {}
    for element in page:
        ele_h3 = element.findChild("h3")
        ele_pre = element.findChild("pre")
        if '入力例' not in str(ele_h3) and '出力例' not in str(ele_h3):
            continue
        if '入力例' in str(ele_h3):
            case = {}
            case["input"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n','\n').lstrip("\n")
        else:
            case["output"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n', '\n').lstrip("\n")
            res.append(case)
    return res
