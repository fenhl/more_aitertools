This Python module provides:

* A subclass of `Queue` which is also an async iterator.
* The `collate` async iterator, which is an async variant of [`heapq.merge`](https://docs.python.org/3/library/heapq.html#heapq.merge) (aka `more_itertools.collate`). Currently does not support `reverse` but does support `key`.
* The `merge` async iterator, which takes an iterable of iterables, and yields items from them in the order they arrive. See the example. Both the outer iterable and the inner iterables may be sync or async.
* The `never` async iterator, which never yields or returns.

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
