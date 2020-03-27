import os
import requests
from bs4 import BeautifulSoup
import pickle
import subprocess
from uroboros.constants import ExitStatus

from communication import ATCODER_ENDPOINT,COOKIE_FILE 
import communication as com

TESTCASES_PATH = "test_case"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = '\033[36m'
COLORRESET = "\033[0m"

def isfloat(parameter):
    if not parameter.isdecimal():
        try:
            float(parameter)
            return True
        except ValueError:
            return False
    else:
        return False

def read_file(file_name):
    """ファイルを読む"""

    testcases = []
    targ_path = os.path.join(TESTCASES_PATH, file_name)
    with open(targ_path, "r") as f:
        while(1):
            st = f.readline().rstrip('\r\n')
            if 'test case' in st:
                testcase = {}
                continue
            if 'input' in st:
                mode = "input"
                testcase[mode] = ""
                continue
            if 'output' in st:
                mode = "output"
                testcase[mode] = ""
                continue        
            if '---fin---' in st:
                testcases.append(testcase)
                continue
            if not st:
                break
            testcase[mode] += st + "\n"
    return testcases

def write_file(file_name, testcases):
    """ファイルを書く"""
    targ_path = os.path.join(TESTCASES_PATH, file_name)
    with open(targ_path, "w") as f:
        for i, q in enumerate(testcases):
            f.write("[test case " + str(i) + "]\n")
            f.write("---input---\n")
            f.write(q["input"])
            f.write("---output---\n")
            f.write(q["output"])
            f.write("---fin---\n")

def scrape_page(problem_id, contest_id, config):
    session = com.make_session(config)
    page = session.get(ATCODER_ENDPOINT + contest_id + 
        "/tasks/" + contest_id + "_" + problem_id)
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
        if 'Sample' not in str(ele_h3):
            continue
        if 'Input' in str(ele_h3):
            case = {}
            case["input"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n','\n')
        else:
            case["output"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n', '\n')
            res.append(case)
    return res


def read_case(problem_id, contest_id, config):
    case_file = problem_id + ".txt"
    if case_file in os.listdir(TESTCASES_PATH):
        cases = read_file(case_file)
    else:
        cases = scrape_page(problem_id,contest_id, config)
        write_file(case_file, cases)
    return cases

def judge(testcases, problem_id, contest_id):
    print(CYAN + "Judging " + contest_id + "_" + problem_id + "..." + COLORRESET)
    res = {"AC":0, "WA":0, "TLE":0}
    for i, case in enumerate(testcases):
        print("case " + str(i+1) + ": ", end="")
        proc = subprocess.Popen("./a.out", stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, shell=True)
        proc.stdin.write(case["input"].encode())
        proc.stdin.flush()
        proc.stdout.flush()
        try:
            proc.wait(2)
            ans = proc.stdout.read().decode().replace("\r\n","\n")
            out = case["output"].replace("\r\n","\n")
            if out == ans:
                res["AC"]+=1
                print(GREEN + "AC" + COLORRESET)
            elif isfloat(out) and isfloat(ans):
                d = abs(float(out)-float(ans))
                r = d / float(out)
                if d <= 0.000001 and r <= 0.000001:
                    res["AC"]+=1
                    print(GREEN + "AC" + COLORRESET)
                else:
                    res["WA"]+=1
                    print(YELLOW + "WA" + COLORRESET)
                    print(RED + " predicted:"+ ans.rstrip('\r\n') + "\n" + 
                        " result:" + out.rstrip('\r\n') + COLORRESET)
            else:
                res["WA"] += 1
                print(YELLOW + "WA" + COLORRESET)
                print(RED + " predicted:"+ ans.rstrip('\r\n') + "\n" + 
                    " result:" + out.rstrip('\r\n') + COLORRESET)
        except:
            res["TLE"]+=1
            print(YELLOW + "TLE" + COLORRESET)
            proc.terminate()
    return ExitStatus.SUCCESS

def testing(problem_id, config):
    filename = "{id}{ext}".format(id=problem_id, ext=config["language"]["filename_ext"])
    contest_id = os.path.basename(os.getcwd())
    res = subprocess.run([config["language"]["compile_cmd"], filename])
    
    if res.returncode != 0:
        return ExitStatus.UNABLE_TO_EXEC

    testcases = read_case(problem_id,contest_id, config)
    return judge(testcases, problem_id, contest_id)