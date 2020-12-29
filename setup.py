from setuptools import setup

setup(
    name="app_watcher",
    version="0.0.1",
    author="Tony H",
    packages=["app_watcher", "app_watcher.utils"],
    include_package_data=True,
    entry_points={"console_scripts": ["app_watcher=app_watcher.__main__:main"]},
)
