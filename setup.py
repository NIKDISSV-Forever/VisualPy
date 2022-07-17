import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.MD', encoding='UTF-8') as f:
    readme = f.read()

setuptools.setup(
    name='VisualPy',
    version='0.1.1',

    description='Cross-platform python interpreter with highlighting, autocompletion and code hints '
                '(Like IPython and BPython)',
    long_description=readme,
    long_description_content_type="text/markdown",

    author='NIKDISSV (Nikita)',
    author_email='nikdissv@proton.me',

    packages=['VPython'],

    python_requires='>=3.8',

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',

        'Environment :: Console',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

        'Topic :: Software Development :: Interpreters',
        'Topic :: Terminals',
        'Topic :: Text Editors',

        'Typing :: Typed'
    ],
    keywords=['ipython', 'bpython', 'vpython', 'highlight', 'interpreter', 'interactive', 'code', 'console']
)
