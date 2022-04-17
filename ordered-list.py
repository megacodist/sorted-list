from __future__ import annotations   # For postponed evaluation of annotations, required CPython 3.8+
from collections.abc import Sequence, Iterator
from typing import Any, Callable


class OrderedList(Sequence):
    def __init__(
        self,
        key: Callable[[Any], Any] = None,
        *items: Any
    ) -> None:
        # Setting the comparer callable...
        self._key = key

        # Initializing the internal list...
        self._items = []
        for item in items:
            keyValue = self._key(item) if self._key else None
            self._items.append(
                (
                    item,
                    keyValue
                )
            )
        if len(self._items):
            self._items.sort(key=lambda item: (item[1], item[0]))

    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, index: int) -> Any:
        return self._items[index]

    def __iter__(self) -> Iterator[OrderedList]:
        # Setting the iterator variable...
        self._iterIndex = 0

        return self
    
    def __next__(self):
        try:
            currIndex = self._iterIndex
            self._iterIndex += 1
            return self._items[currIndex]
        except IndexError:
            raise StopIteration
    
    def __contains__(self, value: object) -> bool:
        return value in self._items
    
    def GetIndex(self, value: Any) -> int | None:
        pass

    def Put(self, value: Any) -> None:
        pass


if (__name__ == '__main__'):
    mm = [1, 2, 3,4 ,5, 6, 7, 8,8, 9,]
    for m in mm:
        print(m)
        mm.pop()
    m = OrderedList()
    sorted()