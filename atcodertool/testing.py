import os
import requests
from bs4 import BeautifulSoup
import pickle
import subprocess
import signal
from uroboros.constants import ExitStatus

from atcodertool.communication import ATCODER_ENDPOINT,COOKIE_FILE 
import atcodertool.communication as com

TESTCASES_PATH = com.INFO_DIR_PATH

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
    with open(targ_path, "w", newline="\n") as f:
        for i, q in enumerate(testcases):
            f.write("[test case " + str(i) + "]\n")
            f.write("---input---\n")
            f.write(q["input"])
            f.write("---output---\n")
            f.write(q["output"])
            f.write("---fin---\n")


def read_case(problem_id, contest_id, config):
    case_file = problem_id + ".txt"
    if case_file in os.listdir(TESTCASES_PATH):
        cases = read_file(case_file)
    else:
        cases = com.scrape_page(problem_id,contest_id, config)
        write_file(case_file, cases)
    return cases

def judge(testcases, problem_id, contest_id, config):
    print(CYAN + "Judging " + contest_id + "_" + problem_id + "..." + COLORRESET)
    for i, case in enumerate(testcases):
        print("case " + str(i+1) + ": ", end="")
        res = compare(case, config)
        if res[0] == "AC":
            print(GREEN + "AC" + COLORRESET)
        elif res[0] == "WA":
            print(YELLOW + "WA" + COLORRESET)
            print(RED + "[output]\n"+ res[1][0].rstrip('\r\n') + "\n" + 
                "[answer]\n" + res[1][1].rstrip('\r\n') + COLORRESET)
        else:
            print(YELLOW + res[0] + COLORRESET)
    return ExitStatus.SUCCESS

def execute(case, config):
    try:
        proc = subprocess.run(config["language"]["exe_cmd"], timeout=2, 
                capture_output=True, text=True, input=case["input"])
    except subprocess.TimeoutExpired:
        return "TLE"
    if proc.returncode != 0:
        return "RE"
    else:
        #out = proc.stdout.replace("\r\n", "\n")
        return proc.stdout#.rstrip("\r\n ")

def compare(case, config):
        out = execute(case, config)
        if out == "TLE":
            return (out, None)
        if out == "RE":
            return (out, None)
        out = out.replace("\r\n", "\n")
        ans = case["output"].replace("\r\n","\n")
        if out == ans:
            return ("AC", None)
        elif isfloat(out) and isfloat(ans) ans float(out) != 0:
            d = abs(float(out)-float(ans))
            r = d / float(out)
            if d <= 0.000001 and r <= 0.000001:
                return ("AC", None)
            else: 
                return ("WA", (out, ans))
        else:
            return ("WA", (out, ans))


def compiling(problem_id, config):
    #print(CYAN + "compiling..." + COLORRESET, end=" ")
    filename = "{id}{ext}".format(id=problem_id, ext=config["language"]["filename_ext"])
    res = subprocess.run([config["language"]["compile_cmd"], config["language"]["compile_opt"], filename],
           capture_output=True, text=True)
    if res.returncode != 0:
        print(YELLOW + "CE" + COLORRESET)
        print(res.stderr)
        return ExitStatus.FAILURE
    #print(GREEN + "SUCCESS!" + COLORRESET)
    return ExitStatus.SUCCESS


def compare_cases(testcases, problem_id, config):
    status = compiling(problem_id, config)
    if status != ExitStatus.SUCCESS:
        return False
    return all(map(lambda case : compare(case, config)[0]=="AC", testcases))

def testing(problem_id, config):
    if config["language"]["compiling"]:
        status = compiling(problem_id, config)
        if status != ExitStatus.SUCCESS:
            return status
    contest_id = os.path.basename(os.getcwd())
    testcases = read_case(problem_id,contest_id, config)
    return judge(testcases, problem_id, contest_id, config)
