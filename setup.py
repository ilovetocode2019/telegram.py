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
    description="An async API wrapper for the Telegram bot API in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ilovetocode",
    url="https://github.com/ilovetocode2019/telegram.py",
    project_urls={
        "Documentation": "https://telegrampy.readthedocs.io",
        "Issue tracker": "https://github.com/ilovetocode2019/telegram.py/issues",
    },
    version=version,
    lisence="MIT",
    packages=["telegrampy", "telegrampy.types", "telegrampy/ext/commands"],
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "docs": [
            "sphinx==3.5.3",
            "sphinx-rtd-theme",
            "sphinxcontrib_trio==1.1.2",
            "sphinxcontrib-websupport",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
)
