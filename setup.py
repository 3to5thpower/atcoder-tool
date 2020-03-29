import setuptools

with open("README.md") as f:
    readme = f.read()

setuptools.setup(
    name="atcoder_tool",
    author="sagoj0_",
    description="test and submit tool for atcoder",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
)