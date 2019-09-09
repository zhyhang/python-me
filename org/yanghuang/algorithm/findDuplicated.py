if __name__ == '__main__':
    inputs = input('please input numbers(separator is blanket):\n')
    nums = inputs.split()
    distinctNums = set()
    for num in nums:
        n = int(num)
        if n < 0:
            n = -n
        if n not in distinctNums:
            distinctNums.add(n)
    print(len(distinctNums))
