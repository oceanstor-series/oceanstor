from setuptools import setup

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name="oceanstor",
    version="1.0.0",
    description="Huawei OceanStor 100D REST Client",
    keywords=["huawei", "storage", "oceanstor", "rest", "client"],
    url="",
    download_url="",
    author="Huawei OceanStor Storage",
    author_email="liulimin5@huawei.com",
    license="BSD 2-Clause",
    packages=["oceanstor"],
    install_requires=["requests"],
    tests_require=['mock'],
    long_description=README_TEXT,
)
