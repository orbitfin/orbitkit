# orbitkit

[![pypi-version]][pypi]

**This project is only for Orbit Technology [https://www.orbitfin.ai/] internal use.**

Full documentation for the project is available at [https://github.com/clown-0726/orbitkit/tree/main/docs][docs].

---

# Overview

`orbitkit` is a powerful and flexible toolkit for enhancing your application.

Some reasons you might want to use `orbitkit`:

* The out-of-box utils' api to use for your application.
* Customizable all the way down - just use few of code to implement file extraction.

----

# Requirements

* Python (3.5, 3.6, 3.7, 3.8, 3.9)
* Django (2.2, 3.0, 3.1, 3.2)

We **highly recommend** and only officially support the latest patch release of
each Python and Django series.

# Installation

Install using `pip`...
```
pip install orbitkit
```

# Example

Let's take a look at a quick example of using `orbitkit` to build your application.

Startup up a new file extraction like so...
```
pip install orbitkit
```

Now edit any python file in your project:

```python
from orbitkit import FileDispatcher

if __name__ == '__main__':
    # Init extractor
    file_dispatcher = FileDispatcher(extractor_config={
        "extract_url": "",
        "aws_access_key_id": "",
        "aws_secret_access_key": ""
    })

    # Configure file info
    file_obj = FileDispatcher.get_params_template()
    file_obj.update({
        'bucket': 'filing-reports',
        'store_path': 'reports-data/test_extract/Prospekt Inv. BankInvest - 2020.09.21 clean.pdf',
        'file_name': '',
        'file_type': 'pdf',
    })

    # Init specific extractor
    extractor = file_dispatcher.init_extractor(file_obj)

    # Start extracting
    # res = extractor.extract()
    res = extractor.extract_timeout()
    print(res)
    print(res['text'])

```

We'd also like to configure `extract_url` as your pleased.

That's it, we're done!

# Documentation & Support

Full documentation for the project is available at [https://github.com/clown-0726/orbitkit/tree/main/docs][docs].

For questions and support, use the [https://github.com/clown-0726/orbitkit/issues] to track.

[pypi-version]: https://img.shields.io/pypi/v/orbitkit.svg
[pypi]: https://pypi.org/project/orbitkit/
