import setuptools
import re

version = ""
with open("pygram/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setuptools.setup(
    name="telegram.py",
    description="An async API wrapper for telegram in python",
    author="Ilovetocode",
    url="https://github.com/ilovetocode2019/telegram.py",
    version=version,
    packages=["pygram", "pygram/ext/commands"],
    extras_require={"docs": ["sphinx==2.4.3", "sphinx-rtd-theme"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)