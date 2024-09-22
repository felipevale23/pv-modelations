from setuptools import setup, find_packages

setup(
    name='pv_modelations',  # Your package name
    version='0.1',  # Version of your package
    author='Felipe Vale',
    author_email='your.email@example.com',
    description='A brief description of your project',
    long_description=open('README.md').read(),  # Use your README file for a detailed description
    long_description_content_type='text/markdown',  # Specify if README is in markdown
    url='https://github.com/felipevale23/pv-modelations',  # URL to the project repo
    packages=find_packages(),  # Automatically find and include all Python packages in the project
    install_requires=[  # External dependencies the project needs
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version requirement
    entry_points={  # Command-line entry points (optional)
        'console_scripts': [
            'src=src.module:main',  # Expose a command that runs a function
        ],
    },
)