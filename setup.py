from setuptools import find_packages, setup

setup(
    name='snouth',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask==1.0',
        'flask-sqlalchemy==2.1',
        'pymongo',
        'flask-jwt-extended',
        'gunicorn',
        'requests'
    ],
)