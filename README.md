# Flypper: feature flags, with a GUI

Flypper is a lightweight feature flag package that ships with a WSGI interface.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `flypper`.

```bash
pip install flypper
```

You might want to install one of the following backends instead:

* [`flypper-redis`](https://github.com/nicoolas25/flypper-redis) to store your flags in Redis
* [`flypper-sqlalchemy`](https://github.com/nicoolas25/flypper-sqlalchemy) to store your flags in a RDBMS using SQL-Alchemy (work in progress)

## Why

Feature flags can be instrumental to how a team ships software.

I have a hard take delegating such a critical part to a third-party.
Also, third-parties tends to grow a bigger feature set than the one I need,
to have a per-seat pricing, and to ask for a [SSO tax](https://sso.tax/).

Flypper aims at providing a simple feature flag library one could integrate
directly to their application as a dependency. The feature set is purposedly
small and will require some light work on your side to integrate.

Differences compared to other similar libraries are:

* A scrappy web UI to manage the flags
* An architecture aimed at being used on backends and front-ends
* An efficient caching mecanism to avoid roundtrip to the database

## Usage

The library works with 3 components:
1. A **storage** backend, storing and retrieving flags in a durable way
2. A **client**, acting as an efficient in-memory cache for reading flags
3. A **context**, making flags consistents during its lifespan

| Components and their roles |
|---|
| ![storage-client-context](https://user-images.githubusercontent.com/163953/138587140-e133ec12-6776-4bee-b80f-851eac7cb6a9.png) |

Here is an example:

```python
from redis import Redis

from flypper import Client as Flypper
from flypper_redis.storage.redis import RedisStorage

# Instanciate a *Storage*
redis_storage = RedisStorage(
    redis=Redis(host="localhost", port=6379, db=0),
    prefix="flypper-demo",
)

# Instanciate a *Client*
flypper = Flypper(storage=redis_storage)

# Query flags' statuses within a *Context*
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

flypper_web_ui = FlypperWebUI(storage=redis_storage)
```

| Web UI |
|---|
| ![web-ui](https://user-images.githubusercontent.com/163953/138586961-d3cb5653-8713-4e3f-a60b-207bc5913a15.png) |

The web UI can then be mounted as you see fit,
for instance via [`DispatcherMiddleware`](https://werkzeug.palletsprojects.com/en/2.0.x/middleware/dispatcher/).

```python
app = DispatcherMiddleware(app, {"/flypper": flypper_web_ui})
```

⚠ Careful, you might need to wrap the `FlypperWebUI` with your own authentication layer,
for instance like [here](https://eddmann.com/posts/creating-a-basic-auth-wsgi-middleware-in-python/).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

### Work in progress you can contribute to

* Testing the web UI with [pytest and selenium](https://pytest-selenium.readthedocs.io/en/latest/user_guide.html)
* Better support prefixes within the web UI, so redirections work
* Write tutorials and recipes in the `docs/`

### Upcoming feature ideas

* Javascript SDK
* Tracking flags usage efficiently
* More storage backends

## Credits

Inspiration was heavily taken from the following projects.

* [flipper](https://github.com/jnunemaker/flipper)
* [unleash](https://github.com/Unleash/unleash)
* [flipper-client](https://github.com/carta/flipper-client)

Many thanks to their authors, maintainers, and contributors.

## License

[MIT](https://choosealicense.com/licenses/mit/)


