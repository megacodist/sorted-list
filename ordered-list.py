from __future__ import annotations   # For postponed evaluation of annotations, required CPython 3.8+
from collections.abc import Sequence, Iterator, Iterable
from typing import Any, Callable, Literal


class OrderedList(Sequence):
    class DataComparerPair(object):
        def __init__(
            self,
            data: Any,
            comparer: Any
        ) -> None:
            self.data = data
            self.comparer = comparer

        def __gt__(self, value: Any) -> bool:
            return self.comparer > value
        
        def __lt__(self, value: Any) -> bool:
            return self.comparer < value
        
        def __ge__(self, value: Any) -> bool:
            return self.comparer >= value
        
        def __le__(self, value: Any) -> bool:
            return self.comparer <= value
        
        def __eq__(self, value: Any) -> bool:
            return self.comparer == value
        
        def __ne__(self, value: Any) -> bool:
            return self.comparer != value


    def __init__(
        self,
        items: Iterable = None,
        collision: Literal['start', 'end', 'ignore'] = 'ignore',
        key: Callable[[Any], Any] = None
    ) -> None:
        # Setting the comparer callable...
        # Instances of this class are dependent to the reference of 'key'. If in the middle of the life cycle of some instances the 'key' refrence
        # becomes deleted, '_usingComparer' will detect and cause 'key' related operations to fail.
        if key:
            self._usingComparer = True
            self._key = key
        else:
            self._usingComparer = False
            self._key = key
        
        # Checking the collision policy...
        POSSIBLE_COLLISION = ['start', 'end', 'ignore']
        if collision not in POSSIBLE_COLLISION:
            raise ValueError("Wrong collision policy. 'collision' must be one of " + str(POSSIBLE_COLLISION)[1:-1])
        
        self._collision = collision

        # Initializing the internal list...
        self._items = []
        for item in items:
            # Creating a new item...
            if self._key:
                newItem = OrderedList.DataComparerPair(
                    data=item,
                    comparer=self._key(item)
                )
            else:
                newItem = item

            # Adding the new item to the underlying list...
            self._items.append(newItem)
        
        if len(self._items):
            if self._key:
                self._items.sort()
            else:
                self._items.sort(key=lambda item: item.comparer)

    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, index: int) -> Any:
        return self._items[index]
    
    def __setitem__(self, index: int, value: Any) -> None:
        raise NotImplemented("You are not allowed to change the underlying list on your own. But instead you can use 'Put' method to put the 'vaue' in its suitable position.")

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
    
    def GetIndex(self, value: Any) -> None | int | slice:
        '''Returns the index of 'value' in the OrderedList. The possible return values are as follow:
        
        ⬤ None: 'value' does not exist in the OrderedList but suitable position is 0 if we wanted to have it in the OrderedList.
        ⬤ zero: 'value' is the first element (index 0) of the OrderedList.
        ⬤ a positive integer: 'value' is at this position in the OrderedList.
        ⬤ a negative integer: 'value' does not exist in the OrderedList but suitable position is the absolue value of this negative integer if we wanted to have it in the OrderedList.
        ⬤ a slice object: more that one 'value' are in the OrderedList and the slice object specifies their positions in the OrderedList.'''
        
        if self._usingComparer:
            value_ = OrderedList.DataComparerPair(value, self._key(value))
        else:
            value_ = value

        # Checking if 'value' must be placed at the end of the list...
        if value_ > self._items[-1]:
            return -len(self._items)
        
        # Checking if 'value' must be placed at the beginning of the list...
        if value_< self._items[0]:
            return None
        
        # Finding the position...
        return self._DoBinSearch(
            value_,
            0,
            len(self._items)
        )

    def Put(
        self,
        value: Any,
        collision: Literal['start', 'end', 'ignore'] = 'ignore',
        lIndex: int = 0,
        rIndex: (None | int) = None
    ) -> None:
        '''Puts 'value' into a correct position in the OrderedList.
        
        If there is the same value(s) in the OrderedList (collision), it is possible to put it just after all equal values (end), just before all equal values (start), or to ignore the value.'''
        
        # Checking lIndex parameter...
        if value < self._items[lIndex]:
            raise ValueError('')
    
    def Merge(
        self,
        item: Iterable[Any],
        collision: Literal['start', 'end', 'ignore'] = 'ignore'
    ) -> None:
        pass

    def _DoBinSearch(
        self,
        value: Any,
        lIndex: int,
        rIndex: int
    ) -> None | int | slice:
        '''Does a binary search for 'value' in the underlying list between the start index of 'lIndex' and the end index of 'rIndex' (both indices are included). The possible return values are as follow:
        
        ⬤ None: 'value' does not exist in the OrderedList but suitable position is 0 if we wanted to have it in the OrderedList.
        ⬤ zero: 'value' is the first element (index 0) of the OrderedList.
        ⬤ a positive integer: 'value' is at this position in the OrderedList.
        ⬤ a negative integer: 'value' does not exist in the OrderedList but suitable position is the absolue value of this negative integer if we wanted to have it in the OrderedList.
        ⬤ a slice object: more that one 'value' are in the OrderedList and the slice object specifies their positions in the OrderedList.'''

        # Checking the stop recursion condition...
        if lIndex + 1 == rIndex:
            # Recursion must be stopped, possible return values are as follow:
            # 1. rIndex                if and only if value == items[rIndex] and value > items[lIndex]
            # 2. lIndex                if and only if value == items[lIndex] and value < items[rIndex]
            # 3. slice(lIndex, rIndex) if and only if value == items[lIndex] and value == items[rIndex]
            # 4. -rIndex               if and only if items[lIndex] < value < items[rIndex]
            if value == self._items[lIndex]:
                if value == self._items[rIndex]:
                    return slice(lIndex, rIndex)
                else:
                    return lIndex
            else:
                if value == self._items[rIndex]:
                    return rIndex
                else:
                    return -rIndex
        
        # Finding the middle index...
        mIndex = (rIndex + lIndex) // 2
        if value > self._items[mIndex]:
            # Searching the upper (right) half...
            self._DoBinSearch(value, mIndex, rIndex)
        elif value < self._items[mIndex]:
            # Searching the lower (left) half...
            self._DoBinSearch(value, lIndex, mIndex)
        else:
            # value === items[mIndex]
            # So searching for a possible slice...

            # Finding possible slice stop...
            rIndex = mIndex + 1
            try:
                while True:
                    if value != self._items[rIndex]:
                        break
                    rIndex += 1
            except IndexError:
                pass

            # Finding possible slice start...
            lIndex = mIndex - 1
            try:
                while True:
                    if value != self._items[lIndex]:
                        break
                    lIndex -= 1
            except IndexError:
                pass
            lIndex += 1

            # Determinning slice or index...
            if rIndex - lIndex > 1:
                return slice(lIndex, rIndex)
            else:
                return mIndex



if (__name__ == '__main__'):
    class Triple:
        def __init__(self, a: float) -> None:
            self._data = (a, 3 * a,)
        
        def __gt__(self, value) -> bool:
            return self._data[1] > value
        
        def __lt__(self, value) -> bool:
            return self._data[1] < value
    
    class NoTriple:
        def __init__(self, a: float) -> None:
            self._data = (a, 3 * a,)
        
        def __gt__(self, value) -> bool:
            return self._data[0] > value
        
        def __lt__(self, value) -> bool:
            return self._data[0] < value

    print(Triple(2) > NoTriple(2))
    print(NoTriple(6) > Triple(2))
    print(Triple(2) > Triple(2.1))
    print(NoTriple(2.1) > NoTriple(2))

    def func():
        return '123'
    
    class mmm:
        def __init__(self, func) -> None:
            self._func = func
        
        def __str__(self) -> None:
            return self._func()
    
    func2 = func
    mm = mmm(func2)

    print(str(mm))
    from time import sleep

    sleep(2)
    del func
    print(str(mm))