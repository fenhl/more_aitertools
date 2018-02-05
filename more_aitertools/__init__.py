import aitertools
import asyncio

class Queue(asyncio.Queue):
    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.get()

async def merge(aiters):
    aiters = await aitertools.aiter(aiters)
    iters = [None]
    nexts = [asyncio.ensure_future(aitertools.anext(aiters))]
    while len(iters) > 0:
        await asyncio.wait(nexts, return_when=asyncio.FIRST_COMPLETED)
        new_iters = []
        completed_iters = set()
        for i, future in enumerate(nexts):
            if future.done():
                try:
                    if iters[i] is None:
                        # new iterator
                        new_iters.append(await aitertools.aiter(future.result()))
                    else:
                        # new item
                        yield future.result()
                    nexts[i] = asyncio.ensure_future(aitertools.anext(aiters if iters[i] is None else iters[i]))
                except StopAsyncIteration:
                    completed_iters.add(i)
        for i in sorted(completed_iters, reverse=True):
            iters.pop(i)
            nexts.pop(i)
        iters += new_iters
        nexts += [asyncio.ensure_future(aitertools.anext(new_iter)) for new_iter in new_iters]
