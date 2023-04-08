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
        'python-hcl2==3.0.5',
        'GitPython==3.1.27',
    ],
    extras_require={
        'dev': [
            'pytest==7.1.3',
            'black==23.3.0',
            'isort==5.12.0',
            'commitizen==2.42.1',
            'flake8==6.0.0',
            'pre-commit==3.2.2',
        ]
    },
    entry_points={'console_scripts': [f'{generator.__name__}=generator.main:main']},
)
