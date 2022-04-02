import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="secure-config-manager",
    version="0.0.1",
    author="Polina Matavina",
    description="Secure config manager. Access app secrets easily without sharing them to public.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulin-mipt/secure-config-manager",
    project_urls={
        "Bug Tracker": "https://github.com/paulin-mipt/secure-config-manager/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.0",
)