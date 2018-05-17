from distutils.core import setup

setup(
    name="pyzulipbot",
    version="0.2",
    license="MIT",
    description="a simple programable zulipbot",
    author="Greg McCoy",
    author_email="greg@gkmc.ca",
    url="https://github.com/gregmccoy/pyzulipbot",
    requires=[
        'zulip_bots',
    ],
    packages = ['pyzulipbot'],
)
