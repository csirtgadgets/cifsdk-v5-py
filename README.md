# Getting Started
## CommandLine
```bash
# this requires python3.6 or higher..

$ apt-get intstall -y libsnappy-dev  # brew install snappy
$ pip3 install geoip2 'cifsdk>=5.0b1,<6.0'
$ export CIF_REMOTE=http://localhost:5000

$ cif --itype url --tags phishing
$ cif -nq example.com
$ cif --profile zeek
..
```

## Python SDK
```python

from pprint import pprint
from cifsdk import search, create

for i in search({'indicator': 'example.com'}):
    pprint(i)


rv = create({'indicator': 'example.com', 'tags': 'phishing', 'group': 'everyone'})


```

# Getting Involved
There are many ways to get involved with the project. If you have a new and exciting feature, or even a simple bugfix, simply [fork the repo](https://help.github.com/articles/fork-a-repo), create some simple test cases, [generate a pull-request](https://help.github.com/articles/using-pull-requests) and give yourself credit!

If you've never worked on a GitHub project, [this is a good piece](https://guides.github.com/activities/contributing-to-open-source) for getting started.

* [How To Contribute](contributing.md)  
* [Project Page](http://csirtgadgets.com/collective-intelligence-framework/)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YZPQXDLNYZZ3W)

# COPYRIGHT AND LICENSE

Copyright (C) 2020 [the CSIRT Gadgets](http://csirtgadgets.com)

Free use of this software is granted under the terms of the [Mozilla Public License (MPLv2)](https://www.mozilla.org/en-US/MPL/2.0/).
