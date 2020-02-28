import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='pyloci',
      version='0.1.1',
      description='Python library for Loc-I',
      url='https://locationindex.org/',
      author='Location Index',
      author_email='locationindex@ga.gov.au',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
      ],
      install_requires=[
         'XlsxWriter',
         'SPARQLWrapper<=1.8.5',
         'rdflib<=4.2.2',
         'python-dotenv<=0.11.0',
         'requests<=2.23.0'
      ],
      packages=setuptools.find_packages(),
      python_requires='>=3.6',
      zip_safe=False)
