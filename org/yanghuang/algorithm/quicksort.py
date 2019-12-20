def quickSort(a: list):
    if a == None or len(a) < 2:
        return
    qsort(a, 0, len(a) - 1)


def qsort(a: list, low: int, high: int):
    if low < high:
        mid = partition(a, low, high)
        qsort(a, low, mid - 1)
        qsort(a, mid + 1, high)


def quickSortIter(a: list):
    if a == None or len(a) < 2:
        return
    positions = [(0, len(a) - 1)]
    while len(positions) > 0:
        lowHigh = positions.pop()
        low = lowHigh[0]
        high = lowHigh[1]
        if low < high:
            mid = partition(a, low, high)
            positions.append((low, mid - 1))
            positions.append((mid + 1, high))


def partition(a: list, low: int, high: int) -> int:
    pivot = a[high]
    i = low - 1
    for j in range(low, high):
        if a[j] < pivot:
            i += 1
            tmp = a[i]
            a[i] = a[j]
            a[j] = tmp
    a[high] = a[i + 1]
    a[i + 1] = pivot
    return i + 1


def sortPrint(a: list):
    print('original list:', a)
    a1 = None
    a2 = None
    if a != None:
        a1 = a.copy()
        a2 = a.copy()
    quickSort(a1)
    print('list after nest quick sort:', a1)
    quickSortIter(a2)
    print('list after loop quick sort:', a2)


if __name__ == '__main__':
    a = [1, 8, 7, 3, 6, 2, 5, 6]
    sortPrint(a)
    a = [1, 1, 2, 2, 3, 3]
    sortPrint(a)
    a = [8, 3]
    sortPrint(a)
    a = [7]
    sortPrint(a)
    a = []
    sortPrint(a)
    a = None
    sortPrint(a)
