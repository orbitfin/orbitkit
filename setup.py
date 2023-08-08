from os.path import dirname, join
from setuptools import setup, find_packages

with open(join(dirname(__file__), 'orbitkit/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name='orbitkit',
    version=version,
    description=(
        'This project is only for Orbit Tech internal use.'
    ),
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author='Lilu Cao',
    author_email='lilu.cao@qq.com',
    maintainer='Lilu Cao',
    maintainer_email='lilu.cao@qq.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/clown-0726/orbitkit',
    classifiers=[
        # 'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "boto3 >= 1.16.0",
        "requests >= 2.12.1",
        "prettytable >= 3.0.0",
        "pytz >= 2022.1",
    ]
)
