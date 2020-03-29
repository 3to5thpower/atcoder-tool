from setuptools import setup, find_packages

with open("requirements.txt") as f:
    req=f.read().splitlines()

setup(
    name="atcoder-tool",
    version="0.1",
    packages=find_packages(),
    install_requires=req,
    entry_points={
        "console_scripts":[
            "atcoder_tool = atcodertool.main:main"
        ]
    }
)