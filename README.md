# Flypper: feature flags, with an GUI

Flypper is a lightweight feature flag package that ships with a WSGI interface.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `flypper`.

```bash
pip install flypper
```

You might want to install one of the following backends instead:

* [`flypper-redis`](https://github.com/nicoolas25/flypper-redis) to store your flags in Redis
* `flypper-sqlalchemy` to store your flags in a RDBMS using SQL-Alchemy (not yet released)

## Usage


The library works with 3 components:
1. A storage backend, storing and retrieving flags in a durable way
2. A client, acting as an efficient in-memory cache for reading flags
3. A context, making flags consistents during its lifespan

Here is an example:

```python
from flypper import Client as Flypper

flypper = Flypper(storage=redis_storage)

with flypper(segment="professionals") as flags:
    if flags.is_enabled("graceful_degradation"):
        skip_that()
    elif flags.is_enabled("new_feature", user="42"):
        do_the_new_stuff()
    else:
        do_the_old_stuff()
```

The web UI acts as a client and only needs a storage:

```python
from flypper.wsgi.web_ui import FlypperWebUI

web_ui = FlypperWebUI(storage=redis_storage)
```

The web UI can then be mounted as you see fit,
for instance via [`DispatcherMiddleware`](https://werkzeug.palletsprojects.com/en/2.0.x/middleware/dispatcher/).

⚠ Careful, you might need to wrap the `FlypperWebUI` with your own authentication layer,
for instance like [here](https://eddmann.com/posts/creating-a-basic-auth-wsgi-middleware-in-python/).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)


