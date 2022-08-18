# Copyright (c) 2022, Megacodist
# All rights reserved.
#
# This source code is licensed under the MIT license found in the LICENSE
# file in the root directory of this source tree.

# Requires Python 3.10+
# For postponed evaluation of annotations, required CPython 3.8+
from __future__ import annotations
from bisect import bisect_right
from collections.abc import Sequence, Iterator, Iterable
from copy import deepcopy
from enum import IntEnum
from typing import Any, Callable


class IntervalError(Exception):
    '''This exception is used to specify an improper interval or an
    operation which cannot be done in the specified interval.
    '''
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class CollisionPolicy(IntEnum):
    '''This enumeration is used when you want to add a value into a sorted
    list which is already in the list (collision). Possible policies are as
    follow:
    
    ⬤ IGNORE: specifies not to put that value into the sorted list.
    ⬤ END: specifies to put that value just after all the same values
    ⬤ START: specifies to put that value just before all the same values
    '''
    IGNORE = 0
    END = 1
    START = 2


class _DataComparerPair(object):
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


class SortedList(Sequence):
    '''SortedList is a sequence-like, iterable, and iterator class. This
    class is not thread safe.
    '''

    def __init__(
            self,
            *,
            cp: CollisionPolicy = CollisionPolicy.IGNORE,
            key: Callable[[Any], Any] = None
            ) -> None:
        '''This is the initializer of the class with two keyword-only
        arguments. The 'cp' parameter accepts a CollisionPolicy which
        defaults to IGNORE. It can be set at any time with 'cp' property.
        The 'key' callable acts like key parameters in Python ecosystem. The
        callable must accepts a value and returns a result as well and if
        it does not provide values will be compared directly without any
        intermediate comparers. This attribute can not be changed. To change
        this attribute, you must instantiate a new sorted list.
        '''
        # Setting the comparer callable...
        self._key: Callable[[Any], Any] = key
        
        # Checking the collision policy...
        if not isinstance(cp, CollisionPolicy):
            raise TypeError("'collision' must be a " + CollisionPolicy.__name__)
        # No error, setting it...
        self._cp: CollisionPolicy = cp

        # Creating the iterator index...
        self._iterIndex: (None | int) = None

        # Initializing the internal list to empty...
        self._items: list[Any] = []
    
    @property
    def items(self) -> list[Any]:
        """Gets or sets the items of this object. It returns a copy of the
        objects in the list as a regular list or sets the underlying list
        with the the sorted version of argument provided.
        """
        return deepcopy(self._items)
    
    @items.setter
    def items(self, __list: list[Any], /) -> None:
        del self._items
        self._items = []
        self.merge(__list)
    
    @property
    def cp(self) -> CollisionPolicy:
        """Gets or sets the collision policy for this object."""
        return self._cp
    
    @cp.setter
    def cp(self, __cp: CollisionPolicy) -> None:
        if not isinstance(__cp, CollisionPolicy):
            raise TypeError(
                "The argument must be an instance of CollisionPolicy")

    def __len__(self) -> int:
        return len(self._items)
    
    def __getitem__(self, __idx: int, /) -> Any:
        if self._key:
            return self._items[__idx].data
        else:
            return self._items[__idx]
    
    def __delitem__(self, __idx: int, /) -> None:
        """Deletes the specified list position (index)."""
        del self._items[__idx]
    
    def __eq__(self, __list: list, /) -> bool:
        return self._items == __list
    
    def __ne__(self, __list: list, /) -> bool:
        return self._items != __list
    
    def __gt__(self, __list: list, /) -> bool:
        return self._items > __list
    
    def __ge__(self, __list: list, /) -> bool:
        return self._items >= __list
    
    def __lt__(self, __list: list, /) -> bool:
        return self._items < __list
    
    def __le__(self, __list: list, /) -> bool:
        return self._items <= __list

    def __iter__(self) -> Iterator[SortedList]:
        # Settingand returning the iterator variable...
        self._iterIndex = 0
        return self
    
    def __next__(self):
        try:
            currIndex = self._iterIndex
            self._iterIndex += 1
            if self._key:
                return self._items[currIndex].data
            else:
                return self._items[currIndex]
        except IndexError:
            raise StopIteration
    
    def __str__(self) -> str:
        if self._key:
            return str([item.data for item in self._items])
        else:
            return str(self._items)
    
    def __contains__(self, value: object) -> bool:
        """Determines that specified value exists in the list or not."""
        if self._key:
            value_ = _DataComparerPair(
                value,
                self._key(value))
        else:
            value_ = value
        existed, _ = self.index(value_)
        return existed
    
    def count(self, __value: Any, /) -> int:
        '''Returns number of occurrences of '__value' in the SortedList.'''
        existed, idx = self.index(__value)
        if existed:
            if isinstance(idx, slice):
                lower, upper, _ = idx.indices(self.__len__())
                return upper - lower
            else:
                return 1
        else:
            return 0
    
    def index(
            self,
            value: Any,
            start: int = 0,
            end: int | None = None
            ) -> tuple[bool, int | slice]:
        '''This method is the backbone of this class. It returns the index of
        'value' in the SortedList. You can specifies an interval in the form of
        [start, end)  to search for index, 'start' is included and 'end' in
        excluded. 'start' and 'end' are defaulted to 0 and None respectively
        which means 0 <= index < len(internal list). If you specify each
        boundary beyond these boundaries, they automatically will be clipped
        to these deafults. If there are the same value at the boundary of the
        specified interval, this method returns an index or a slice object
        that might lie outside of the interval.

        It returns a pair, the first element specifies whether value existed
        in the list (True if existed). If existed (True), the second value
        will be an integer or a slice object. If there is one such value, the
        second element will be its index in the list, or if there are multiple
        such values the second element will be a slice object. If not existed
        (False) the second element will be the proper insertion position of
        the value in the list.
        
        Exceptions:
        ⬤ TypeError: at least one of the 'start' or 'end' parameters got
        improper value
        ⬤ ValueError: 'start' was evaluated to be greater than 'end' or
        'value' is not compatible with 'key' comparer
        ⬤ IntervalError: it is impossible to put 'value' in this interval
        [start, end)'''

        # Checking boundaries & initializing left & right indexes...
        # Checking 'start' parameter...
        if not isinstance(start, int):
            raise TypeError("'start' must be an integer")
        # Clipping out of boundary indices for 'start'...
        if start < 0:
            start = 0
        
        # Checking 'end' parameter...
        if end is None:
            end = len(self._items)
        elif not isinstance(end, int):
            raise TypeError("'end' must be an integer or None")
        else:
            # Clipping out of boundary indices for 'end'...
            if end > len(self._items):
                end = len(self._items)
        
        # Checking the interval...
        if start > end:
            raise ValueError("'start' was evaluated to be greater than 'end'")
        
        # Getting comparer...
        try:
            if self._key:
                value_ = _DataComparerPair(
                    value,
                    self._key(value))
            else:
                value_ = value
        except Exception:
            raise ValueError("'value' is not compatible with 'key' comparer.")
        
        # Finding index...
        idx = bisect_right(self._items, value_, start, end, key=self._key)
        if idx == 0:
            return False, 0
        else:
            if self._items[idx - 1] > value_:
                raise IntervalError(
                    "Impossible to add 'value' at the specified interval")
            elif self._items[idx - 1] == value_:
                # Looking for the start of the possible slice...
                start = idx - 1
                while start >= 0:
                    if self._items[start] != value_:
                        break
                    start -= 1
                start += 1
                if (idx - start) > 1:
                    return True, slice(start, idx)
                else:
                    return True, start
            else:
                return False, idx
    
    def add(
            self,
            value: Any,
            start: int = 0,
            end: int | None = None,
            cp: CollisionPolicy | None = None
            ) -> None | int:
        '''Adds 'value' into its correct position in the SortedList. It
        accepts a 'cp' parameter which can be any CollisionPolicy value
        and defaults to None. None means use object default CollisionPolicy
        or you can specifies the policy for this add operation. This method
        returns the insertion position as an integer or None if IGNORE
        CollisionPolicy prevented the insertion. You can specify an interval
        like 'index' method.
        '''
        # Determining the collision policy for this operation...
        if not ((cp is None) or isinstance(cp, CollisionPolicy)):
            raise TypeError("'cp' must be a CollisionPolicy")
        if cp is None:
            cp = self._cp
        
        # Getting comparer...
        try:
            if self._key:
                value_ = _DataComparerPair(
                    value,
                    self._key(value))
            else:
                value_ = value
        except Exception:
            raise ValueError("'value' is not compatible with 'key' comparer.")

        existed, idx = self.index(value_, start, end)
        if existed:
            if cp == CollisionPolicy.IGNORE:
                return None
            if isinstance(idx, slice):
                lower, upper, _ = idx.indices(self.__len__())
            else:
                # idx is an integer
                lower, upper = idx, idx + 1
            if cp == CollisionPolicy.END:
                self._items.insert(upper, value_)
                return upper
            else:
                # cp == CollisionPolicy.START
                self._items.insert(lower, value_)
                return lower
        else:
            self._items.insert(idx, value_)
            return idx
    
    def merge(
            self,
            items: Iterable[Any],
            cp: CollisionPolicy | None = None
            ) -> None:
        """Merges an interable of items into their suitable positions in
        the list. You can specify a custom collision policy for this
        operation.
        """
        # Determining the collision policy for this operation...
        if not ((cp is None) or isinstance(cp, CollisionPolicy)):
            raise TypeError("'cp' must be a CollisionPolicy")
        if cp is None:
            cp = self._cp
        
        # Preparing the iterable...
        if self._key:
            items_ = [
                _DataComparerPair(
                    data=item,
                    comparer=self._key(item))
                for item in items]
        else:
            items_ = list(items)
        items_.sort()
        
        # Inserting the iterable into the list...
        start = 0
        for item in items_:
            existed, idx = self.index(item, start)
            if existed:
                if cp != CollisionPolicy.IGNORE:
                    if isinstance(idx, slice):
                        lower, upper, _ = idx.indices(self.__len__())
                    else:
                        lower, upper = idx, idx + 1
                    if cp == CollisionPolicy.END:
                        self._items.insert(upper, item)
                        start = upper
                    else:
                        self._items.insert(lower, item)
                        start = lower
            else:
                self._items.insert(idx, item)
                start = idx
