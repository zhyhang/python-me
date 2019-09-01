# coding=UTF-8
import sys


def makeTree(preOrders: list, inOrders: list) -> list:
    '''
    make a tree by pre-order travel chars and in-order travel chars
    :param preOrders: a list of pre-order of tree char sequence
    :param inOrders: a list of in-order of tree char sequence
    :return:a tree by list

    a tree node by a 3 elements list
    []:0-node value
    []:1-left subtree, None when empty
    []:2-right subtree, None when empty
    '''
    root = []
    if len(inOrders) > 0:
        root.append(preOrders[0])
        midIndex = inOrders.index(root[0])
        leftSubTree = makeTree(preOrders[1:], inOrders[:midIndex])
        if len(leftSubTree) > 0:
            root.append(leftSubTree)
        else:
            root.append(None)
        rightSubTree = makeTree(preOrders[midIndex + 1:], inOrders[midIndex + 1:])
        if len(rightSubTree) > 0:
            root.append(rightSubTree)
        else:
            root.append(None)
    return root


def mirrorTree(root: list):
    if len(root) == 0:
        return
    tmp = root[1]
    root[1] = root[2]
    root[2] = tmp
    if root[1] != None:
        mirrorTree(root[1])
    if root[2] != None:
        mirrorTree(root[2])


def postOrderTravelTree(root: list, travales: list):
    if len(root) == 0:
        return
    if root[1] != None:
        postOrderTravelTree(root[1], travales)
    if root[2] != None:
        postOrderTravelTree(root[2], travales)
    travales.append(root[0])


if __name__ == '__main__':
    print(sys.argv)
    # tree = makeTree(['A', 'B', 'D', 'E', 'C', 'F'], ['D', 'B', 'E', 'A', 'C', 'F'])
    # tree = makeTree([], [])
    # tree = makeTree(['A'], ['A'])
    # tree = makeTree(['A','B','C'], ['C','B','A'])
    # tree = makeTree(['A','B','C'], ['A','B','C'])
    tree = makeTree(['h', 'i', 'k', 'l', 'j', 'm', 'o', 'n'], ['k', 'i', 'l', 'h', 'o', 'm', 'j', 'n'])

    print(tree)
    postOrders = []
    postOrderTravelTree(tree, postOrders)
    print(postOrders)

    mirrorTree(tree)
    print(tree)
    postOrders = []
    postOrderTravelTree(tree, postOrders)
    print(postOrders)
