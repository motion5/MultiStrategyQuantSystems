import setuptools

setuptools.setup(
    name="quantlib",
    version="0.1",
    description="code lib created from the HangUkQuant course",
    url="#",
    author="motion5",
    install_requires=[
        "opencv-python",
        "pandas",
        "numpy",
        "ta-lib",
        "yfinance",
        "matplotlib",
        "openpyxl",
        "pandas-stubs",
        "types-beautifulsoup4",
        "types-requests",
    ],
    author_email="",
    packages=setuptools.find_packages(),
    zip_safe=False,
)
