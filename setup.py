from setuptools import setup

setup(
    name="pg-fdw-ai",
    version="1.0.0",
    description="PostgreSQL Foreign Data Wrapper for OpenAI API integration",
    py_modules=["openai_fdw"],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
    ],
)
