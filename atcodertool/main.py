import os, subprocess

from uroboros import Command
from uroboros.constants import ExitStatus

import atcodertool.testing as test
import atcodertool.communication as com
import atcodertool.config as conf


class RootCommand(Command):
    name = "atcoder_tool"
    long_description = "this is helper for testing and submitting on atcoder"

    def build_option(self, parser):
        """Add optional arguments"""
        parser.add_argument('--version', action='store_true', default=False, help='Print version')
        return parser

    def run(self, args):
        if args.version:
            print("{name} v{version}".format(
                name=self.name, version="1.0.0"))
        else:
            self.print_help()
        return ExitStatus.SUCCESS


class Run(Command):
    """Sub command of root"""
    name = "run"
    short_description = "normal execution"
    def build_option(self, parser):
        parser.add_argument("problem_id")
        return parser

    def run(self, args):
        config = conf.read_config()
        filename = "{id}{ext}".format(id=args.problem_id, ext=config["language"]["filename_ext"])
        res = subprocess.run([config["language"]["compile_cmd"], filename])
        if res.returncode == 0:
            res = subprocess.check_output(["./a.out"])
            print(res.decode())
        return ExitStatus.SUCCESS


class Test(Command):
    name = "test"
    short_description = "testing codes."

    def build_option(self, parser):
        parser.add_argument("problem_id", help="problem name (e.g. a)")
        return parser

    def run(self, args):
        config = conf.read_config()
        return test.testing(args.problem_id, config)


class New(Command):
    name = "new"
    short_description = "create new contest."

    def build_option(self, parser):
        parser.add_argument("contest_id",help="contest name (e.g. abc042)")
        parser.add_argument("-p","--problems",default=6, type=int)
        return parser

    def run(self, args):
        config = conf.read_config()
        dirname = args.contest_id
        subprocess.run(["mkdir", dirname])
        subprocess.run(["mkdir","{dir}/test_case".format(dir=dirname)])
        alphabets = [chr(ord("a") + i) for i in range(26)]
        for i in range(args.problems):
            c = alphabets[i]
            filename = "{id}{ext}".format(id=c, ext=config["language"]["filename_ext"])
            with open(dirname + "/" + filename,"x") as f:
                f.write(config["template"]["template"])
                f.close()
    
        return ExitStatus.SUCCESS

class Login(Command):
    name = "login"
    short_description = "log in to atcoder."

    def run(self, args):
        if os.path.exists(com.COOKIE_FILE):
            print("you have already logged in atcoder.")
            return ExitStatus.UNABLE_TO_EXEC
        com.new_session(conf.read_config())
        return ExitStatus.SUCCESS

class Submit(Command):
    name = "submit"
    short_description = "submit source codes to atcoder."

    def build_option(self, parser):
        parser.add_argument("problem_id", help="problem name (e.g. a)")
        parser.add_argument("-f", "--force", action="store_true")
        return parser

    def run(self, args):
        return submitting(args.problem_id, not args.force)
        
def submitting(problem_id, testing):
    config = conf.read_config()
    contest_id = os.path.basename(os.getcwd())
    filename = "{id}{ext}".format(id=problem_id, ext=config["language"]["filename_ext"])

    if testing:
        testcase = test.read_case(problem_id, contest_id, config)
        res = test.compare_cases(testcase, problem_id, config)
        if not res:
            print("Some sample was wrong answer.")
            return ExitStatus.FAILURE
    
    with open(filename) as f:
        codes = f.read()

    status = com.submit(codes, problem_id, contest_id, config)
    if status == ExitStatus.SUCCESS:
        subprocess.run(["xdg-open", com.ATCODER_ENDPOINT+contest_id+"/submissions/me"])
        
    return status        

class Logout(Command):
    name = "logout"
    short_description = "log out from atcoder."
    def run(self, args):
        os.remove(com.COOKIE_FILE)
        print("you logged out from atcoder.")
        return ExitStatus.SUCCESS

# Create command tree
root_cmd = RootCommand()
root_cmd.add_command(Login())
root_cmd.add_command(New())
root_cmd.add_command(Test())
root_cmd.add_command(Run())
root_cmd.add_command(Submit())
root_cmd.add_command(Logout())

if __name__ == '__main__':
    exit(root_cmd.execute())

def main():
    exit(root_cmd.execute())