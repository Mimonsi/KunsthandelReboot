from setuptools import setup, find_packages

with open("requirements.txt") as file:
    requirements = file.readlines()
setup(
    name='Kunsthandel Reboot',
    version='1.0b5', # a = alpha, b = beta, rc = release candidate
    packages=find_packages(),
    url='http://webgadgets.de',
    license='',
    author='kosch104',
    author_email='Konsicrafter@web.de',
    description='Web Database Application for Managing Items',
    include_package_data=True,
    install_requires=requirements
)
