from setuptools import setup

setup(
    name="atcoder-tool",
    version="0.1",
    install_requires=["requests", "beautifulsoup4", "bs4", "uroboros", "toml", "lxml"],
    entry_points={
        "console_scripts":[
            "atcoder_tool = atcodertool.main:main"
        ]
    }
)