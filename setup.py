from setuptools import setup, find_packages

setup(
    name='orbitkit',
    version='0.0.1',
    description=(
        'This project is only for orbit internal use.'
    ),
    long_description=open('README.rst').read(),
    author='Lilu Cao',
    author_email='lilu.cao@qq.com',
    maintainer='Lilu Cao',
    maintainer_email='lilu.cao@qq.com',
    license='BSD License',
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
    install_requires=[
    ]
)
