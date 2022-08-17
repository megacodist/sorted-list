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