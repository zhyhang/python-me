# coding=UTF-8

def search(a, key):
    low = 0
    high = len(a) - 1
    while low <= high:
        mid = (low + high) // 2
        if a[mid] == key:
            return mid
        elif a[mid] < key:
            low = mid + 1
        else:
            high = mid - 1
    return -1


intValues = (1, 2, 3, 5, 7, 9, 10, 10, 13)
print("search(7, in "+str(intValues)+" index is: "+str(search(intValues, 7)))
print("search(3, in "+str(intValues)+" index is: "+str(search(intValues, 3)))
print("search(13, in "+str(intValues)+" index is: "+str(search(intValues, 13)))
print("search(10, in "+str(intValues)+" index is: "+str(search(intValues, 10)))
print("search(15, in "+str(intValues)+" index is: "+str(search(intValues, 15)))
