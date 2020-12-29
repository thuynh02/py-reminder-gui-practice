from setuptools import setup

setup(
    name="app_watcher",
    version="0.0.1",
    author="Tony H",
    packages=["app_watcher"],
    package_dir={"app_watcher": "utils"},
    install_requires=[
        "psutil=5.7.2",
        "pyahocorasick=1.4.0",
        "pyyaml=5.3.1",
        "pysimplegui=4.32.1",
    ],
    entry_points={"console_scripts": ["app_watcher=app_watcher.__main__:main"]},
)
