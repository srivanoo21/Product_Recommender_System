from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="PRODUCT RECOMMENDER",
    version="0.1",
    author="Anoop",
    packages=find_packages(),
    install_requires = requirements,
)