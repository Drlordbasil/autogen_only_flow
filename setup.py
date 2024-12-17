from setuptools import setup, find_packages

setup(
    name="autogen_flow",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "jinja2",
        "aiofiles",
        "pytest",
        "pytest-asyncio",
        "requests",
        "pyautogen",
        "httpx",
        "matplotlib",
        "yfinance",
        "pathlib",
        "typing"
    ],
    python_requires=">=3.12",
)
