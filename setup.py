from setuptools import setup, find_packages


long_description = open('README.md').read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '0.2.0'

setup(
    name='HuBMAPy',
    version=version,
    url='https://github.com/ccb-hms/HuBMAPy',
    description='A package to query the HuBMAP Human Reference Atlas Ontology',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rafael Goncalves, Center for Computational Biomedicine, Harvard Medical School',
    author_email='rafael_goncalves@hms.harvard.edu',
    license='MIT',
    install_requires=requirements,
    packages=find_packages(),
    package_data={'hubmapy': ['resources/*']},
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    python_requires=">=3",
)
