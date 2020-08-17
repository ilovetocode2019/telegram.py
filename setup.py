import setuptools
import re

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = ""
with open("telegrampy/__init__.py") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)

setuptools.setup(
    name="telegram.py",
    description="An async API wrapper for telegram in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ilovetocode",
    url="https://github.com/ilovetocode2019/telegram.py",
    project_urls={
        "Documentation": "https://telegrampy.readthedocs.io",
        "Issue tracker": "https://github.com/ilovetocode2019/telegram.py/issues",
    },
    version=version,
    packages=["telegrampy", "telegrampy/ext/commands", "telegrampy/ext/conversations"],
    install_requires=requirements,
    extras_require={
        "docs": [
            "sphinx==2.4.3",
            "sphinx-rtd-theme",
            "sphinxcontrib_trio==1.1.1",
            "sphinxcontrib-websupport",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
