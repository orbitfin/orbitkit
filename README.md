# [orbitkit][docs]

[![pypi-version]][pypi]

**This project is only for Orbit Technology internal use.**

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
    file_obj = FileDispatcher.get_params_template()
    file_obj['bucket'] = 'vision-filemgt-dev'
    file_obj['store_path'] = 'user-2/a14983bc-0779-471a-89e2-7a83d8cfc92b.docx'
    file_obj['file_name'] = 'a14983bc-0779-471a-89e2-7a83d8cfc92b'
    file_obj['file_type'] = 'docx'
    file_dispatcher = FileDispatcher(file_obj=file_obj, extractor_config={
        "extract_url": ""
    })

    # Execute
    # res = file_dispatcher.to_extract()
    res = file_dispatcher.to_extract_timeout()
    print(res)

```

We'd also like to configure `extract_url` as your pleased.

That's it, we're done!

# Documentation & Support

Full documentation for the project is available at [https://github.com/clown-0726/orbitkit/tree/main/docs][docs].

For questions and support, use the [https://github.com/clown-0726/orbitkit/issues] to track.

[pypi-version]: https://img.shields.io/pypi/v/orbitkit.svg
[pypi]: https://pypi.org/project/orbitkit/
