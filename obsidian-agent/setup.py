from setuptools import setup, find_packages

setup(
    name='obsidian-agent',
    version='0.1.0',
    description='CLI and library for processing Obsidian vault notes',
    author='Malachi',
    packages=['agent'],
    install_requires=[
        'openai>=1.0.0',
        'python-frontmatter>=1.0.0',
        'python-dotenv>=1.0.0',
        'click>=8.0.0'
    ],
    entry_points={
        'console_scripts': [
            'obsidian-agent=run:cli'
        ]
    }
)
