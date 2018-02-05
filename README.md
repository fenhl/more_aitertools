This Python module provides the `merge` async iterator, which takes an async iterator of async iterators, and yields items from them in the order they arrive.

# Example

```python
>>> import aitermerge
>>> import aitertools
>>> import asyncio
>>> async def slow_count(seconds):
...     async for i in aitertools.count():
...         yield i
...         await asyncio.sleep(seconds)
... 
>>> async def slow_counts(limit):
...     for seconds in range(1, limit + 1):
...         yield slow_count(seconds)
... 
>>> sync(aitertools.alist(aitertools.islice(aitermerge.merge(slow_counts(3)), 10)))
[0, 0, 0, 1, 1, 2, 3, 1, 2, 4]
```
