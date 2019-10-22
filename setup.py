import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twitter-sync",
    version="0.0.2",
    author="Ilya Pupko",
    description="Python command-line script to download (or sync) and create markdown copy of tweets (for static sites).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ILAsoft/TwitterStatic",
    install_requires=["python-twitter"],
    packages=setuptools.find_packages(),
    #package_data={'': ["TwitterSyncSettings.sample"]},
    scripts=['TwitterSync.py'],
    platforms="OS Independent",
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)