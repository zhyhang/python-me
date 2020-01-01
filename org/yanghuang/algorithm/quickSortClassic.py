def sort(a: list):
    if a == None or len(a) < 2:
        return
    qsort(a, 0, len(a) - 1)


def qsort(a: list, low: int, high: int):
    if low < high:
        print("partition")
        pos = partitionImproved(a, low, high)
        qsort(a, low, pos - 1)
        qsort(a, pos + 1, high)


def sortIter(a: list):
    if a == None or len(a) < 2:
        return
    stack = [[0, len(a) - 1]]
    while len(stack) > 0:
        lh = stack.pop()
        low = lh[0]
        high = lh[1]
        if low < high:
            print("partition")
            pos = partitionImproved(a, low, high)
            stack.append([low, pos - 1])
            stack.append([pos + 1, high])


def partition(a: list, low: int, high: int) -> int:
    pivotPos = high
    pivot = a[pivotPos]
    i = low
    j = high - 1
    while i < j:
        while a[i] <= pivot and i < j:
            i += 1
        a[pivotPos] = a[i]
        a[i] = pivot
        pivotPos = i
        while a[j] >= pivot and i < j:
            j -= 1
        a[pivotPos] = a[j]
        a[j] = pivot
        pivotPos = j
    return pivotPos


# 10,9,13,8,6,11
# one partition:
#   i=0,j=5,pivot=11
#   while i -> i=2,j=5,13>11 -> 10,9,13,8,6,13
#   while j -> i=2,j=4,6<11 -> 10,9,6,8,6,13
#   while i -> i=4,j=4 -> 10,9,6,8,11,13
def partitionImproved(a: list, low: int, high: int) -> int:
    i = low
    j = high
    pivot = a[j]
    while i < j:
        while a[i] <= pivot and i < j:
            i += 1
        a[j] = a[i]
        print("\tin partition(i->j) i =", i, ", j =", j, ", temp result", a)
        while a[j] >= pivot and i < j:
            j -= 1
        a[i] = a[j]
        print("\tin partition(j->i) i =", i, ", j =", j, ", temp result", a)
    a[i] = pivot
    return i


if __name__ == '__main__':
    a = [10, 9, 13, 8, 6, 11]
    # a=[7,6,5,4,3,2,1]
    # a=[1,2,3,4,5,6,7]
    # sort(a)
    sortIter(a)
    print("final", a)
