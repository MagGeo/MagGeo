from setuptools import setup, find_packages

setup(
    name='maggeo',
    version='0.2.0',
    author='Fernando Benitez-Paez, Urška Demšar, Jed Long, Ciaran Beggan',
    author_email='Fernando.Benitez@st-andrews.ac.uk',
    description='A Python library for annotating GPS trajectories with Swarm satellite geomagnetic data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MagGeo/MagGeo-Annotation-Program',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'scipy>=1.7.0',
        'matplotlib>=3.4.0',
        'viresclient>=0.11.0',
        'chaosmagpy>=0.11.0',
        'tqdm>=4.60.0',
        'requests>=2.25.0',
        'pyyaml>=5.4.0',
        'pooch>=1.3.0',
        'xarray>=0.18.0',
        'netcdf4>=1.5.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
            'mypy>=0.910',
        ],
        'notebooks': [
            'jupyter>=1.0.0',
            'jupyterlab>=3.0.0',  
            'ipywidgets>=7.6.0',
        ],
        'geo': [
            'cartopy>=0.19.0',
            'geopandas>=0.9.0',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9', 
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Animal Movement Analytics',
        'Topic :: Scientific/Engineering :: Data Fusion',
        'Topic :: Scientific/Engineering :: Geomagnetism',
        'Topic :: Scientific/Engineering :: Data Science Ecology',
        'Topic :: Scientific/Engineering :: Animal tracking',
    ],
    python_requires='>=3.8',
    keywords='GPS, Swarm, satellite, geomagnetic, data fusion, animal tracking',
    entry_points={
        'console_scripts': [
            'maggeo=maggeo.core:main',
        ],
    },
)