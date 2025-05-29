from setuptools import setup, find_packages

setup(
    name="pyscope",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'astropy',
        'astroplan',
        'astroquery',
        'numpy',
        'scipy',
        'click',
        'pytest',
        'pytest-cov',
        'matplotlib',
        'photutils',
        'ccdproc'  # Add ccdproc dependency
    ],
)
