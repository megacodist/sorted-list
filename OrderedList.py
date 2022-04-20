# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the LICENSE file in the root directory of this source tree.


from __future__ import annotations   # For postponed evaluation of annotations, required CPython 3.8+
from collections.abc import Sequence, Iterator, Iterable
from enum import IntEnum
from typing import Any, Callable


class CollisionPolicy(IntEnum):
    '''This enumeration is used when you want to put a value into an ordered list which is already in the list (collision). Possible policies are as follow:
    
    ⬤ ingonre: specifies not to put that value into the ordered list.
    ⬤ end: specifies to put that value just after all the same values
    ⬤ start: specifies to put that value just before all the same values'''
    ignore = 0
    end = 1
    start = 2


class OrderedList(Sequence):
    '''OrderedList is a sequence-like, iterable, and iterator class'''
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
        collision: CollisionPolicy = CollisionPolicy.ignore,
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
        if not isinstance(collision, CollisionPolicy):
            raise TypeError("'collision' must be a " + CollisionPolicy.__name__)
        # No error, setting it...
        self._collision = collision

        # Creating the iterator index...
        self._iterIndex: (None | int) = None

        # Initializing the internal list to empty...
        self._items = []

    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, index: int) -> Any:
        if self._usingComparer:
            return self._items[index].data
        else:
            return self._items[index]
    
    def __setitem__(self, index: int, value: Any) -> None:
        raise NotImplemented("You are not allowed to change the underlying list on your own. But instead you can use 'Put' method to put the 'vaue' in its suitable position.")

    def __iter__(self) -> Iterator[OrderedList]:
        # Settingand returning the iterator variable...
        self._iterIndex = 0
        return self
    
    def __next__(self):
        try:
            currIndex = self._iterIndex
            self._iterIndex += 1
            if self._usingComparer:
                return self._items[currIndex].data
            else:
                return self._items[currIndex]
        except IndexError:
            raise StopIteration
    
    def __str__(self) -> str:
        if self._usingComparer:
            return str([item.data for item in self._items])
        else:
            return str(self._items)
    
    def __contains__(self, value: object) -> bool:
        index_ = self.index(value)

        if index_ is None:
            return False
        elif isinstance(index_, slice):
            return True
        elif isinstance(index_, int):
            if index_ < 0:
                return False
            else:
                return True
        else:
            # Something went wrong, reporting a warning...
            pass
    
    def count(self, value: Any) -> int:
        '''Returns number of occurrences of 'value' in the OrderedList.'''
        index_ = self.index(value)

        if index_ is None:
            return 0
        elif isinstance(index_, slice):
            startIndex, stopIndex, _ = index_.indices(self.__len__)
            return stopIndex - startIndex
        elif isinstance(index_, int):
            if index_ < 0:
                return 0
            else:
                return 1
        else:
            # Something went wrong, reporting error...
            pass
    
    def index(
        self,
        value: Any,
        start: int = 0,
        end: int | None = None
    ) -> None | int | slice:
        '''Returns the index of 'value' in the OrderedList. The possible return values are as follow:
        
        ⬤ None: 'value' does not exist in the OrderedList but suitable position is 0 if we wanted to have it in the OrderedList.
        ⬤ zero: 'value' is the first element (index 0) of the OrderedList.
        ⬤ a positive integer: 'value' is at this position in the OrderedList.
        ⬤ a negative integer: 'value' does not exist in the OrderedList but suitable position is the absolue value of this negative integer if we wanted to have it in the OrderedList.
        ⬤ a slice object: more that one 'value' are in the OrderedList and the slice object specifies their positions in the OrderedList.'''

        # Checking boundaries & initializing lent & right indexes...
        # Checking 'start' parameter...
        if not isinstance(start, int):
            raise TypeError("'start' must be an integer")
        
        if start < 0:
            raise ValueError(
                'E1001',
                "'start' can not be less than 0"
            )
        
        lIndex = start
        
        # Checking 'end' parameter...
        if end is None:
            rIndex = len(self._items) - 1
        elif not isinstance(end, int):
            raise TypeError("'end' must be an integer or None")
        else:
            rIndex = end
            if end >= len(self._items):
                raise ValueError(
                    'E1002',
                    "'end' parameter exceeds the list length"
                )
        
        if lIndex > rIndex:
            raise ValueError(
                'E1003',
                "'start' must not be greater than 'end'"
            )
        
        # Getting comparer...
        if self._usingComparer:
            value_ = OrderedList.DataComparerPair(value, self._key(value))
        else:
            value_ = value
        
        # Checking if 'value' must be placed at the beginning of the interval...
        if value_< self._items[lIndex]:
            try:
                if value_ < self._items[lIndex - 1]:
                    raise ValueError(
                        'E1101',
                        "Inserting 'value' into this interval make list inconsistent"
                    )
            except IndexError:
                pass

            if lIndex:
                return -lIndex
            else:
                return None
        # Checking if 'value' must be placed at the end of the interval...
        elif value_ > self._items[rIndex]:
            try:
                if value_ > self._items[rIndex]:
                    raise ValueError(
                        'E1101',
                        "Inserting 'value' into this interval make list inconsistent"
                    )
            except IndexError:
                pass
            return -rIndex - 1 
        # Checking if the interval has got only one element...
        elif lIndex == rIndex:
            return lIndex
        # Checking if 'value' is at the beginning of the interval...
        elif value_ == self._items[lIndex]:
            return self._LookForSlice(lIndex)
        # Checking if 'value' is at the end of the interval...
        elif value_ == self._items[rIndex]:
            return self._LookForSlice(rIndex)
        # Checking if the interval has got two elements...
        elif lIndex + 1 == rIndex:
            return -rIndex        
        # Finding the position recursively...
        else:
            return self._DoBinSearch(
                value_,
                lIndex + 1,
                rIndex - 1
            )

    def Put(
        self,
        value: Any,
        collision: None | CollisionPolicy = None
    ) -> None | int:
        '''Puts 'value' into its correct position in the OrderedList. It accepts a 'collision' parameter which can be any CollisionPolicy value and defaults to None. None means use
        object CollisionPolicy or you can specifies the policy for this put operation. This method returns the insertion position as an integer or it returns None if ignore
        CollisionPolicy prevented the insertion.'''
        
        # Checking collision parameter...
        if collision is None:
            # Using default (object-level) collision...
            collision = self._collision
        elif not isinstance(collision, CollisionPolicy):
            raise TypeError("'collision' must be an instance of CollisionPolicy")
        
        # Getting value...
        if self._usingComparer:
            value_ = self._key(value)
        else:
            value_ = value
        
        # Getting the index of 'value' in the list...
        index_ = self.index(value)

        if index_ is None:
            self._items.insert(0, value_)
            return 0
        elif isinstance(index_, int):
            if index_ < 0:
                position = abs(index_)
                self._items.insert(position, value_)
                return position
            else:
                lower = index_
                upper = index_ + 1
        elif isinstance(index_, slice):
            lower, upper, _ = index_.indices(self.__len__)
        else:
            # Something went wrong.
            # Logging a warning...
            pass

        if collision == CollisionPolicy.ignore:
            return None
        elif collision == CollisionPolicy.start:
            self._items.insert(lower, value_)
            return lower
        else:
            self._items.insert(upper, value_)
            return upper
    
    def Merge(
        self,
        items: Iterable[Any],
        collision: CollisionPolicy = CollisionPolicy.ignore
    ) -> None:
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

    def _LookForSlice(
        self,
        index: int
    ) -> int | slice:
        value = self._items[index]

        # Looking for the start of the possible slice...
        start = index - 1
        try:
            while True:
                if value == self._items[start]:
                    start -= 1
                else:
                    break
        except IndexError:
            pass
        start += 1

        # Looking for the stop of the possible slice...
        stop = index + 1
        try:
            while True:
                if value == self._items[stop]:
                    stop += 1
                else:
                    break
        except IndexError:
            pass

        # Deciding between index or slice...
        if stop - start > 1:
            return slice(start, stop)
        else:
            if index:
                return index
            else:
                return None

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
        # There are two stop recursion conditions...
        # 1. lIndex == rIndex
        # 2. lIndex + 1 == rIndex
        if lIndex == rIndex:
            # First stop recursion condition fulfilled...
            if value < self._items[lIndex]:
                return -lIndex
            elif value > self._items[rIndex]:
                return -rIndex - 1
            else:
                # value == self._items[lIndex]
                return lIndex
        elif lIndex + 1 == rIndex:
            # Second stop recursion condition fulfilled...
            # 1. None ------------------------ if and only if value <  items[lIndex] and lIndex == 0
            # 2. -lIndex ===================== if and only if value <  items[lIndex] and lIndex >  0
            # 3. lIndex ---------------------- if and only if value == items[lIndex] and value <  items[rIndex]
            # 4. slice(lIndex, rIndex + 1) === if and only if value == items[lIndex] and value == items[rIndex]
            # 5. -rIndex --------------------- if and only if value >  items[lIndex] and value <  items[rIndex]
            # 6. rIndex ====================== if and only if value >  items[lIndex] and value == items[rIndex]
            # 7. -rIndex - 1 ----------------- if and only if value >  items[lIndex] and value >  items[rIndex]
            if value < self._items[lIndex]:
                if lIndex == 0:
                    return None
                elif lIndex > 0:
                    return -lIndex
                else:
                    # This case is impossible, reporting a warning...
                    pass
            elif value == self._items[lIndex]:
                if value < self._items[rIndex]:
                    return lIndex
                elif value == self._items[rIndex]:
                    return slice(lIndex, rIndex + 1)
                else:
                    # This case is impossible, reporting a warning...
                    pass
            else:
                # value > self._items[lIndex]
                if value < self._items[rIndex]:
                    return -rIndex
                elif value == self._items[rIndex]:
                    return rIndex
                else:
                    # value > self._items[rIndex]
                    return -rIndex - 1
        
        # No stop recursion conditions fulfilled...
        # Continuing recursion...
        # Finding the middle index...
        mIndex = (rIndex + lIndex) // 2

        if value > self._items[mIndex]:
            # Searching the upper (right) half...
            return self._DoBinSearch(value, mIndex, rIndex)
        elif value < self._items[mIndex]:
            # Searching the lower (left) half...
            return self._DoBinSearch(value, lIndex, mIndex)
        else:
            # value === items[mIndex]
            # So searching for a possible slice...
            return self._LookForSlice(mIndex)



if (__name__ == '__main__'):
    ol = OrderedList(collision=CollisionPolicy.end)
    ol.Put(3)