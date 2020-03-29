import os, sys
import pickle
import requests
from bs4 import BeautifulSoup
from uroboros import ExitStatus
import toml
import getpass
import config as conf

ATCODER_ENDPOINT = "https://atcoder.jp/contests/"
COOKIE_FILE = os.path.expanduser(conf.read_config()["session"]["cookie_file_path"])
LOGIN_URL = "https://atcoder.jp/login"

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
    
    tar = ATCODER_ENDPOINT + contest_id + "/submit"

    html = session.get(tar)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "lxml")
    csrf_token = soup.find(attrs={"name": "csrf_token"}).get("value")

    submit_info = {
        "data.TaskScreenName": contest_id + "_" + problem_id,
        "csrf_token": csrf_token,
        "data.LanguageId": int(config["language"]["lang_id"]),
        "sourceCode": codes
    }
    res = session.post(tar, data=submit_info)
    res.raise_for_status()
    if res.status_code != 200:
        print("Failed to submit source codes.")
        print("HTTP status code is {res}".format(res=res))
        return ExitStatus.FAILURE
    return ExitStatus.SUCCESS

