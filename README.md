This Python package is intended as an add-on to [`aioitertools`](https://github.com/jreese/aioitertools), filling some gaps in its API. It provides:

* A subclass of `Queue` which is also an async iterator.
* The `collate` async iterator, which is an async variant of [`heapq.merge`](https://docs.python.org/3/library/heapq.html#heapq.merge) (aka [`more_itertools.collate`](https://more-itertools.readthedocs.io/en/latest/api.html#more_itertools.collate)). Currently does not support `reverse` but does support `key`.
* The `consume` coroutine, which is an async variant of [`more_itertools.consume`](https://more-itertools.readthedocs.io/en/latest/api.html#more_itertools.consume). It takes an iterable (sync or async) and an optional number `n` (defaults to infinity), and advances it by `n` steps, dropping the yielded values. If the iterable has fewer than `n` items remaining, it is consumed entirely, no exception is raised.
* The `merge` async iterator, which takes an iterable of iterables, and yields items from them in the order they arrive. See the example. Both the outer iterable and the inner iterables may be sync or async.
* The `never` async iterator, which never yields or returns.
* The `tuple` coroutine, which takes an iterable and collects it into a tuple, similar to `aioitertools.list` and `aioitertools.set`.
* The `wait` async iterator, which takes an iterable (sync or async) of futures, and yields results from the front of the iterable as soon as they become available. Using this is similar to calling `asyncio.wait` in `return_when=ALL_COMPLETED` mode and taking the first return value, except it can handle an empty iterable, `.result()` does not have to be called, futures near the start can be used before later futures become available, and futures yielded from the iterable are started before continuing the iteration.

Python 3.6 is required.

# Example

```python
>>> import aitertools
>>> import asyncio
>>> import more_aitertools
>>> async def slow_count(seconds):
...     async for i in aitertools.count():
...         yield i
...         await asyncio.sleep(seconds)
... 
>>> async def slow_counts(limit):
...     for seconds in range(1, limit + 1):
...         yield slow_count(seconds)
... 
>>> sync(aitertools.alist(aitertools.islice(more_aitertools.merge(slow_counts(3)), 10)))
[0, 0, 0, 1, 1, 2, 3, 1, 2, 4]
```
