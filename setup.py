import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), 'r') as fh:
    long_description = fh.read()

requirementPath = os.path.join(here, 'requirements.txt')
install_requires = [] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name='word2Tex',
    version='0.0.11',
    author='Roshan Nanu',
    author_email='roshan.nanu@gmail.com',
    description='package for moving manuscripts from Word to LaTeX',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/nubs01/word2Tex',
    license='MIT',
    packages=setuptools.find_packages(),
    entry_points = {
        'console_scripts': [
            'cite2Tex=word2Tex.cite2Tex:main',
            'fixBibTex=word2Tex.fixBibTex:main',
            'doi2bib=word2Tex.doi2bib:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License'],
    keywords=('word2Tex cite2Tex fixBibTex bibtex latex Word citation '
              'cite convert'),
    python_requires='>=3.6',
    install_requires=install_requires,
    include_package_data=True,
    package_data={}
)




