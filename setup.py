from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hebrew-gdex',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Automated extraction of Good Dictionary Examples (GDEX) for Hebrew using unsupervised clustering',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/hebrew-gdex',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'stanza>=1.11.0',
        'scikit-learn>=1.3.0',
        'numpy>=2.0.0',
        'tqdm>=4.67.0',
        'pyyaml>=6.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Hebrew',
    ],
    python_requires='>=3.12',
)