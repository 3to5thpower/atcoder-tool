from setuptools import setup

setup(
    name="atcoder_tool",
    install_requires=["requests", "beautifulsoup4", "uroboros", "toml", "lxml"],
    entry_points={
        "console_scripts":[
            "atcoder_tool = atcoder_tool.atcoder_tool:main"
        ]
    }
)