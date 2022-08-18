# A sorted list for Python
Have you ever needed to keep a bunch of items in a specified order? For example file system items are usually shown in alphabetical order or to show events chronologically. In all such circumstances a sorted list would ease coding.

```
>>> from sorted_list import SortedList
>>> sl = SortedList()
>>> sl.add(3)
0
>>> print(sl)
[3]
>>> sl.add(5)
1
>>> print(sl)
[3, 5]
>>> sl.add(2)
0
>>> print(sl)
[2, 3, 5]
```
## SortedList
SortedList is a sequence-like, iterable, and iterator class. This class is not thread safe.
## Collisions
When you want to add a value to the sorted list and there is already the same value, or a value which is evaluated to be the same, this situation is called collision. This module offers three ways to deal with the collisions and aggregate them into the ```CollisionPolicy``` enumeration:
1. IGNORE: The value will be ignored and will not be inserted into the list.
2. END: The value will be inserted at the end of all the same values.
3. START: The value will be inserted at the end of all the same values.
## The initializer
### ```sorted_list.SortedList.__init__(self, *, cp: CollisionPolicy = CollisionPolicy.IGNORE, key: Callable[[Any], Any] = None)```:
This is the initializer of the class with two keyword-only arguments. The 'cp' parameter accepts a CollisionPolicy which defaults to IGNORE. It can be set at any time with 'cp' property. The 'key' callable acts like [key parameters](https://docs.python.org/3/howto/sorting.html#key-functions) in Python ecosystem. The callable must accepts a value and returns a result as well and if it does not provide values will be compared directly without any intermediate comparers. This attribute can not be changed. To change this attribute, you must instantiate a new sorted list.
## Properties
### ```sorted_list.SortedList.items```:
Gets or sets the items of this object. It returns a copy of the objects in the list as a regular list or sets the underlying list with the the sorted version of argument provided.
### ```sorted_list.SortedList.cp```:
Gets or sets the collision policy for this object at any time.
## Methods
### ```sorted_list.SortedList.count(__value: Any, /) -> int```:
Returns number of occurrences of '__value' in the SortedList.
### ```sorted_list.SortedList.index(value: Any, start: int = 0, end: int | None = None) -> tuple[bool, int | slice]```:
This method is the backbone of this class. It returns the index of 'value' in the SortedList. You can specifies an interval in the form of [start, end)  to search for index, 'start' is included and 'end' in excluded. 'start' and 'end' are defaulted to 0 and None respectively which means 0 <= index < len(internal list). If you specify each boundary beyond these boundaries, they automatically will be clipped to these deafults. If there are the same value at the boundary of the specified interval, this method returns an index or a slice object that might lie outside of the interval.

It returns a pair, the first element specifies whether value existed in the list (True if existed). If existed (True), the second value will be an integer or a slice object. If there is one such value, the second element will be its index in the list, or if there are multiple such values the second element will be a slice object. If not existed (False) the second element will be the proper insertion position of the value in the list.
        
Exceptions:
* __TypeError__: at least one of the 'start' or 'end' parameters got improper value
* __ValueError__: 'start' was evaluated to be greater than 'end' or 'value' is not compatible with 'key' comparer
* __IntervalError__: it is impossible to put 'value' in this interval [start, end)
### ```sorted_list.SortedList.add(value: Any, start: int = 0, end: int | None = None, cp: CollisionPolicy | None = None) -> None | int```:
Adds 'value' into its correct position in the SortedList. It accepts a 'cp' parameter which can be any CollisionPolicy value and defaults to None. None means use object default CollisionPolicy or you can specifies the policy for this add operation. This method returns the insertion position as an integer or None if IGNORE CollisionPolicy prevented the insertion. You can specify an interval like 'index' method.
### ```sorted_list.SortedList.merge(items: Iterable[Any], cp: CollisionPolicy | None = None) -> None```
Merges an interable of items into their suitable positions in the list. You can specify a custom collision policy for this operation.
## Operators
### len
It is possible to get the length of the underlying list with the builtin len function.
```
>>> from sorted_list import SortedList
>>> sl = SortedList()
>>> len(sl)
0
>>> sl.items = [5, 0, 2]
>>> len(sl)
3
>>> print(sl)
[0, 2, 5]
```
### Subscript notation
You can get a value at the specified index by subscript notation:
```
>>> sl = SortedList()
>>> sl.merge([3, 5, 0, 0])
>>> print(sl)
[0, 3, 5]
>>> sl[0]
0
>>> sl[1]
3
>>> sl[2]
5
>>> sl[3]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "D:\Programming\Exercises\Python\sorted-list\sorted_list.py", line 136, in __getitem__
    return self._items[__idx]
IndexError: list index out of range
```
### del
Deletes the specified list position (index).
### Arithmetic comparisons
Instances of this class can be compared with any regular lists with arithmetic comparison operators of <, >, <=, =>. ==, and !=.