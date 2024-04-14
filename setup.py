from setuptools import setup, find_packages

setup(
    name="sqlite-shift",
    version="0.2.0",
    author="Akarsh T S",
    author_email="ts.akarsh@gmail.com",
    description="A framework for managing SQLite database migrations, inspired by Django.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Akarsh-TS/sqlite-shift",
    license="Apache License 2.0",  # Specify the license here
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Database Management Tool",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "sqlite-shift=sqlite_shift.cli:cli",
        ],
    },
    install_requires=[
        'click',        
    ],
)
