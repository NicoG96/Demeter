from setuptools import setup

setup(
    name="Demeter",
    version="1.0.0",
    author="Nico Gonzalez",
    author_email="NicoG96@gmail.com",
    packages=["demeter"],
    license="LICENSE",
    url="https://github.com/NicoG96/Demeter",
    description="Automate the branching stuff with Python!",
    long_description=open("README.md").read(),
    install_requires=[
        "termcolor",
        "pyfiglet",
        "GitPython",
        "pygithub",
    ],
    entry_points={"console_scripts": ["demeter=demeter:demeter_cli"]}
)