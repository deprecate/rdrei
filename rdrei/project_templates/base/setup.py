try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='${appname}',
    version='0.1',
    description='',
    author='',
    author_email='',
    #url='',
    install_requires=[
        "rdrei",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
)
