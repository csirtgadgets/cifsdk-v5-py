from setuptools import setup, find_packages
import os
import sys
import versioneer


# https://www.pydanny.com/python-dot-py-tricks.html
if sys.argv[-1] == 'test':
    test_requirements = [
        'pytest',
        'coverage',
        'pytest_cov',
    ]
    try:
        modules = map(__import__, test_requirements)

    except ImportError as e:
        err_msg = e.message.replace("No module named ", "")
        msg = "%s is not installed. Install your test requirments." % err_msg
        raise ImportError(msg)

    r = os.system('py.test test -v --cov=cifsdk --cov-fail-under=65 && '
                  'xenon -b B -m A -a A -e "cifsdk/_version*,cifsdk/client/http/utils.py,cifsdk/cli.py,cifsdk/client/zeromq/base.py" cifsdk')
    if r == 0:
        raise SystemExit

    raise RuntimeError('tests failed')

setup(
    name="cifsdk",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="CIFv5 SDK",
    long_description="CIFv5 Software Development Kit",
    url="https://github.com/csirtgadgets/cifsdk-v5",
    license='MPL2',
    classifiers=[
        "Topic :: System :: Networking",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python"
    ],
    keywords=['network', 'security'],
    author="Wes Young",
    author_email="wes@csirtgadgets.com",
    packages=find_packages(exclude='test'),
    install_requires=[
        'ujson',
        'tornado',
        'msgpack',
        'pyzmq',
        'python-snappy',
        'arrow',
        'csirtg-dt',
        'csirtg-re',
        'csirtg-peers',
        'csirtg-spamhaus',
        'csirtg-indicator',
        'csirtgsdk',
    ],
    entry_points={
        'console_scripts': [
            'cif=cifsdk.cli:main'
        ]
    },
    test_suite="test"
)
