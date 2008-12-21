try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='rdrei',
    version='0.1',
    description='A web framework built on top of Werkzeug.',
    author='Pascal Hartig',
    author_email='phartig@rdrei.net',
    #url='',
    install_requires=[
        "Werkzeug",
        "jinja2",
        "Babel",
        "sqlalchemy",
        "beaker",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    scripts = ['rdrei-admin.py'],
)
