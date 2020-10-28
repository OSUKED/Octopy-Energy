import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="octopyenergy",
    version="0.0.1",
    author="Ayrton Bourn",
    author_email="ayrtonbourn@outlook.com",
    description="Python client for the Octopus energy API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AyrtonB/Octopy-Energy", 
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)