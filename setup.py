from setuptools import setup, find_packages


setup(
    name="pytrade",
    version="0.1.0",

    author="Simon Garisch",
    author_email="gatman946 at gmail.com",

    description="Backtesting in Python.",
    long_description=open("README.md").read(),

    packages=find_packages(exclude=('tests',)),
    install_requires=[],
)
