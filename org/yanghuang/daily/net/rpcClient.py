import socket
import math


# 构造tcp请求数据帧
def buildSendData(srvIndex: int) -> bytes:
    sendData = bytearray()
    # 1个字节，version
    sendData.append(1)
    # 1个字节，命令类型-1(0xff)代表服务命令
    sendData.append(0xff)
    # 4个字节，seq
    sendData.append(0)
    sendData.append(0)
    sendData.append(0)
    sendData.append(1)
    # 2个字节，rpc service中index值
    sendData.append((serviceIndex >> 8) & 0xff)
    sendData.append(serviceIndex & 0xff)
    # 1个字节，data type，0代表无data数据
    sendData.append(0)
    return sendData


# 检查接收到数据是否合法
def checkValidRecv(recvData: bytes, srvIndex: int) -> bool:
    if len(recvData) < 12:
        return False
    if recvData[0] != 0x1:
        return False
    recvSrvIndex = (recvData[6] << 8) | recvData[7]
    if srvIndex != recvSrvIndex:
        return False
    if recvData[8] != 0x0 and recvData[8] != 0x1 and recvData[8] != 0xff:
        return False
    return True


# 接收到的是否异常数据
def excepted(recvData: bytes) -> bool:
    return recvData[8] == 0x1


# 计算接收到tcp帧中真正数据的长度
def dataLength(recvData: bytes) -> int:
    length = (recvData[9] & 0x7f)
    if recvData[9] > 0x7f:
        length = (length | ((recvData[10] & 0x7f) << 7))
    else:
        return length
    if recvData[10] > 0x7f:
        length = (length | ((recvData[11] & 0x7f) << 14))
    else:
        return length
    if recvData[11] > 0x7f:
        length = (length | ((recvData[12] & 0x7f) << 21))
    else:
        return length
    if recvData[12] > 0x7f:
        length = (length | ((recvData[13] & 0x7f) << 28))
    return length


def lengthStoreBytes(dataLen: int) -> int:
    return math.ceil(math.log(dataLen, 127))


# 完整读取所有数据，包括头信息，放在recvData参数中，返回数据正文长度
def readAllData(sock: socket, srvIndex: int, recvData: bytearray) -> int:
    headerPacket = sock.recv(2048)
    if not checkValidRecv(headerPacket, srvIndex):
        raise Exception('invalid data header!')
    recvData.extend(headerPacket)
    dataLen = dataLength(headerPacket)
    lenBytes = lengthStoreBytes(dataLen)
    totalLen = dataLen + 9 + lenBytes
    while len(recvData) < totalLen:
        recvData.extend(sock.recv(2048))
    return dataLen


# 读取消息正文，且变为utf8文本返回，若server端异常，则抛出Exception('server exception',server exception msg)
def readDataText(sock: socket, srvIndex: int) -> str:
    recvData = bytearray()
    dataLen = readAllData(sock, srvIndex, recvData)
    retText = str(recvData[len(recvData) - dataLen:], encoding='UTF-8')
    if excepted(recvData):
        raise Exception('server exception', retText)
    return retText


if __name__ == '__main__':
    serviceIndex = int(30000)
    sock = socket.socket()
    sock.connect(('192.168.152.13', 7200))
    try:
        sock.send(buildSendData(serviceIndex))
        recvDataText = readDataText(sock, serviceIndex)
        print(recvDataText)
    except Exception as e:
        if len(e.args) == 2 and 'server exception' == e.args[0]:
            print('server error:')
            print(e.args[1])
        else:
            raise
    finally:
        sock.close()
