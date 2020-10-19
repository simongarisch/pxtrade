from setuptools import setup, find_packages


setup(
    name="pxtrade",
    version="0.2.0",
    install_requires=[
        "pandas>=1.1.1",
        "pandas_datareader>=0.9.0",
        "ipython==7.15.0",
        "cufflinks>=0.17.3",
    ],

    author="Simon Garisch",
    author_email="gatman946@gmail.com",
    url="https://github.com/simongarisch/pxtrade",

    description="A multi currency, event driven backtester written in Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",

    packages=find_packages(exclude=("tests",)),
)
