from setuptools import find_packages, setup

import generator

setup(
    name=generator.__name__,
    version=generator.__version__,
    author='Chris',
    author_email='goabonga@pm.me',
    description='generate terragrunt manifest from terraform module.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'python-hcl2==4.3.5',
        'GitPython==3.1.43',
    ],
    extras_require={
        'dev': [
            'pytest==8.3.3',
            'pytest-cov==5.0.0',
            'black==24.8.0',
            'isort==5.13.2',
            'commitizen==3.29.0',
            'flake8==7.1.1',
            'pre-commit==3.8.0',
        ]
    },
    entry_points={'console_scripts': [f'{generator.__name__}=generator.main:main']},
)
