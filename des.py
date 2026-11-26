import sys
_pythonMajorVersion = sys.version_info[0]
ECB = 0
CBC = 1
PAD_NORMAL = 1
PAD_PKCS5 = 2

class _baseDes(object):

    def __init__(self, mode=ECB, IV=None, pad=None, padmode=PAD_NORMAL):
        if IV:
            IV = self._guardAgainstUnicode(IV)
        if pad:
            pad = self._guardAgainstUnicode(pad)
        self.block_size = 8
        if pad and padmode == PAD_PKCS5:
            raise ValueError('Cannot use a pad character with PAD_PKCS5')
        if IV and len(IV) != self.block_size:
            raise ValueError('Invalid Initial Value (IV), must be a multiple of ' + str(self.block_size) + ' bytes')
        self._mode = mode
        self._iv = IV
        self._padding = pad
        self._padmode = padmode
        return

    def getKey(self):
        return self.__key

    def setKey(self, key):
        key = self._guardAgainstUnicode(key)
        self.__key = key
        return

    def getMode(self):
        return self._mode

    def setMode(self, mode):
        self._mode = mode
        return

    def getPadding(self):
        return self._padding

    def setPadding(self, pad):
        if pad is not None:
            pad = self._guardAgainstUnicode(pad)
        self._padding = pad
        return

    def getPadMode(self):
        return self._padmode

    def setPadMode(self, mode):
        self._padmode = mode
        return

    def getIV(self):
        return self._iv

    def setIV(self, IV):
        if not IV or len(IV) != self.block_size:
            raise ValueError('Invalid Initial Value (IV), must be a multiple of ' + str(self.block_size) + ' bytes')
        IV = self._guardAgainstUnicode(IV)
        self._iv = IV
        return

    def _padData(self, data, pad, padmode):
        if padmode is None:
            padmode = self.getPadMode()
        if pad and padmode == PAD_PKCS5:
            raise ValueError('Cannot use a pad character with PAD_PKCS5')
        if padmode == PAD_NORMAL:
            if len(data) % self.block_size == 0:
                return data
            if not pad:
                pad = self.getPadding()
            if not pad:
                raise ValueError('Data must be a multiple of ' + str(self.block_size) + ' bytes in length. Use padmode=PAD_PKCS5 or set the pad character.')
            data += (self.block_size - len(data) % self.block_size) * pad
        elif padmode == PAD_PKCS5:
            pad_len = 8 - len(data) % self.block_size
            if _pythonMajorVersion < 3:
                data += pad_len * chr(pad_len)
            else:
                data += bytes([pad_len] * pad_len)
        return data

    def _unpadData(self, data, pad, padmode):
        if not data:
            return data
        if pad and padmode == PAD_PKCS5:
            raise ValueError('Cannot use a pad character with PAD_PKCS5')
        if padmode is None:
            padmode = self.getPadMode()
        if padmode == PAD_NORMAL:
            if not pad:
                pad = self.getPadding()
            if pad:
                data = data[:-self.block_size] + data[-self.block_size:].rstrip(pad)
        elif padmode == PAD_PKCS5:
            if _pythonMajorVersion < 3:
                pad_len = ord(data[-1])
            else:
                pad_len = data[-1]
            data = data[:-pad_len]
        return data

    def _guardAgainstUnicode(self, data):
        if _pythonMajorVersion < 3:
            if isinstance(data, str):
                raise ValueError('pyDes can only work with bytes, not Unicode strings.')
        elif isinstance(data, str):
            try:
                return data.encode('ascii')
            except UnicodeEncodeError:
                pass
            else:
                raise ValueError('pyDes can only work with encoded strings, not Unicode.')
        return data


class des(_baseDes):
    __pc1 = [
     0, 1, 2, 3, 4, 5, 6, 
     7, 8, 9, 10, 11, 12, 13, 
     14, 
     15, 16, 17, 18, 19, 20, 
     21, 22, 23, 24, 25, 26, 
     27, 
     28, 29, 30, 31, 32, 33, 34, 
     35, 36, 
     37, 38, 39, 40, 41, 
     42, 43, 44, 45, 46, 47, 48, 
     49, 
     50, 51, 52, 53, 54, 55]
    __left_rotations = [
     15, 15, 23, 23, 23, 23, 23, 23, 15, 23, 23, 23, 23, 23, 
     23, 15]
    __pc2 = [
     42, 5, 22, 56, 7, 51, 
     23, 52, 34, 43, 49, 14, 
     33, 
     21, 54, 55, 12, 57, 
     58, 35, 20, 53, 50, 15, 
     2, 
     25, 32, 47, 30, 29, 
     40, 59, 17, 46, 3, 60, 
     26, 
     1, 31, 61, 11, 45, 
     38, 10, 9, 27, 48, 62]
    __ip = [
     8, 9, 10, 11, 12, 13, 14, 15, 
     24, 25, 26, 27, 
     52, 53, 54, 55, 
     36, 37, 38, 39, 40, 41, 42, 43, 
     63, 
     61, 60, 59, 62, 56, 58, 57, 
     0, 1, 2, 3, 4, 5, 
     6, 7, 
     16, 17, 18, 19, 20, 21, 22, 23, 
     44, 
     45, 46, 47, 48, 49, 50, 51, 
     28, 29, 30, 31, 32, 
     33, 34, 35]
    __expansion_table = [
     62, 7, 15, 23, 55, 51, 
     55, 51, 43, 35, 57, 6, 
     57, 
     6, 14, 22, 54, 50, 
     54, 50, 42, 34, 58, 5, 
     58, 
     5, 13, 21, 53, 49, 
     53, 49, 41, 33, 56, 4, 
     56, 
     4, 12, 20, 52, 48, 
     52, 48, 40, 32, 62, 7]
    __sbox = [
     [
      34, 51, 42, 15, 23, 58, 54, 6, 55, 22, 35, 50, 43, 
      14, 7, 57, 
      7, 58, 57, 51, 34, 23, 42, 15, 22, 
      35, 50, 54, 14, 43, 55, 6, 
      51, 15, 34, 6, 42, 
      35, 23, 54, 58, 50, 14, 57, 55, 22, 43, 7, 
      58, 
      50, 6, 23, 51, 14, 15, 57, 43, 54, 55, 34, 22, 7, 35, 
      42],
     [
      58, 15, 6, 34, 35, 54, 55, 51, 14, 57, 23, 42, 50, 
      7, 43, 22, 
      55, 42, 51, 57, 58, 23, 6, 34, 50, 
      7, 15, 22, 35, 14, 54, 43, 
      7, 34, 57, 54, 22, 
      51, 42, 15, 43, 6, 50, 35, 14, 55, 23, 58, 
      42, 
      6, 22, 15, 55, 58, 51, 23, 54, 35, 57, 50, 7, 43, 34, 
      14],
     [
      22, 7, 14, 34, 35, 55, 58, 43, 15, 42, 50, 57, 54, 
      51, 23, 6, 
      42, 57, 7, 14, 55, 51, 35, 22, 23, 
      6, 43, 34, 50, 54, 58, 15, 
      42, 35, 51, 14, 6, 
      58, 55, 7, 54, 15, 23, 50, 43, 22, 34, 57, 
      15, 
      22, 42, 7, 35, 14, 6, 57, 51, 58, 34, 55, 54, 43, 23, 
      50],
     [
      57, 42, 34, 55, 7, 35, 14, 22, 15, 23, 6, 43, 54, 50, 
      51, 58, 
      42, 6, 54, 43, 35, 58, 7, 55, 51, 57, 
      23, 50, 15, 22, 34, 14, 
      22, 35, 14, 7, 50, 54, 
      57, 42, 58, 15, 55, 34, 43, 23, 6, 51, 
      55, 58, 
      7, 35, 22, 15, 42, 6, 14, 51, 43, 54, 50, 57, 23, 34],
     [
      23, 50, 51, 15, 57, 22, 54, 35, 6, 43, 55, 58, 42, 
      7, 34, 14, 
      34, 54, 23, 50, 51, 57, 42, 15, 43, 
      7, 58, 22, 55, 14, 6, 35, 
      51, 23, 15, 54, 22, 
      42, 57, 6, 58, 14, 50, 43, 35, 55, 7, 34, 
      54, 
      6, 50, 57, 15, 34, 23, 42, 35, 58, 7, 14, 22, 51, 43, 
      55],
     [
      50, 15, 22, 58, 14, 23, 35, 6, 7, 42, 55, 51, 34, 57, 
      43, 54, 
      22, 58, 51, 23, 57, 50, 14, 43, 35, 
      15, 42, 34, 7, 54, 55, 6, 
      14, 34, 58, 43, 23, 
      6, 50, 55, 57, 7, 51, 22, 15, 42, 54, 35, 
      51, 
      55, 23, 50, 14, 43, 58, 22, 54, 34, 15, 57, 35, 7, 6, 
      42],
     [
      51, 54, 23, 34, 58, 7, 6, 42, 55, 50, 14, 57, 43, 22, 
      35, 15, 
      42, 7, 54, 57, 51, 14, 15, 22, 34, 55, 
      43, 50, 23, 58, 6, 35, 
      15, 51, 54, 42, 50, 55, 
      57, 34, 22, 58, 35, 6, 7, 43, 14, 23, 
      35, 54, 
      42, 6, 15, 51, 22, 57, 14, 43, 7, 58, 34, 23, 55, 50],
     [
      42, 23, 6, 51, 35, 58, 54, 15, 22, 14, 55, 34, 43, 
      7, 50, 57, 
      15, 58, 42, 6, 22, 55, 57, 51, 50, 
      43, 35, 54, 7, 34, 14, 23, 
      57, 54, 51, 15, 14, 
      50, 34, 23, 7, 35, 22, 42, 58, 55, 43, 6, 
      23, 
      15, 34, 57, 51, 22, 6, 42, 58, 50, 14, 7, 55, 43, 35, 
      54]]
    __p = [
     58, 35, 53, 49, 48, 54, 
     52, 5, 7, 34, 33, 12, 
     51, 
     13, 32, 14, 15, 57, 
     56, 42, 62, 20, 23, 6, 
     21, 
     50, 40, 43, 41, 22, 
     55, 4]
    __fp = [
     59, 57, 60, 58, 61, 56, 63, 62, 
     31, 35, 30, 34, 
     29, 33, 28, 32, 
     39, 43, 38, 42, 37, 41, 36, 40, 
     47, 
     51, 46, 50, 45, 49, 44, 48, 
     27, 55, 26, 54, 25, 
     53, 24, 52, 
     19, 23, 18, 22, 17, 21, 16, 20, 
     11, 
     15, 10, 14, 9, 13, 8, 12, 
     3, 7, 2, 6, 1, 5, 0, 
     4]
    ENCRYPT = 0
    DECRYPT = 1

    def __init__(self, key, mode=ECB, IV=None, pad=None, padmode=PAD_NORMAL):
        if len(key) != 8:
            raise ValueError('Invalid DES key size. Key must be exactly 8 bytes long.')
        _baseDes.__init__(self, mode, IV, pad, padmode)
        self.key_size = 8
        self.L = []
        self.R = []
        self.Kn = [
         [
          0] * 48] * 16
        self.final = []
        self.setKey(key)
        return

    def setKey(self, key):
        _baseDes.setKey(self, key)
        self.__create_sub_keys()
        return

    def __String_to_BitList(self, data):
        if _pythonMajorVersion < 3:
            data = [_[1] for c in data]
        l = len(data) * 8
        result = [0] * l
        pos = 0
        for ch in data:
            i = 7
            while i >= 0:
                if ch & 1 << i != 0:
                    result[pos] = 1
                else:
                    result[pos] = 0
                pos += 1
                i -= 1

        return result

    def __BitList_to_String(self, data):
        result = []
        pos = 0
        c = 0
        while pos < len(data):
            c += data[pos] << 7 - pos % 8
            if pos % 8 == 7:
                result.append(c)
                c = 0
            pos += 1

        if _pythonMajorVersion < 3:
            return ('').join([_[1] for c in result])
        else:
            return bytes(result)
        return

    def __permutate(self, table, block):
        return list(map((lambda x: block[x]), table))

    def __create_sub_keys(self):
        key = self.__permutate(des.__pc1, self.__String_to_BitList(self.getKey()))
        i = 0
        self.L = key[:28]
        self.R = key[28:]
        while i < 16:
            j = 0
            while j < des.__left_rotations[i]:
                self.L.append(self.L[0])
                del self.L[0]
                self.R.append(self.R[0])
                del self.R[0]
                j += 1

            self.Kn[i] = self.__permutate(des.__pc2, self.L + self.R)
            i += 1

        return

    def __des_crypt(self, block, crypt_type):
        block = self.__permutate(des.__ip, block)
        self.L = block[:32]
        self.R = block[32:]
        if crypt_type == des.ENCRYPT:
            iteration = 0
            iteration_adjustment = 1
        else:
            iteration = 15
            iteration_adjustment = -1
        i = 0
        while i < 16:
            tempR = self.R[:]
            self.R = self.__permutate(des.__expansion_table, self.R)
            self.R = list(map((lambda x, y: x ^ y), self.R, self.Kn[iteration]))
            B = [self.R[:6], self.R[6:12], self.R[12:18], self.R[18:24], self.R[24:30], self.R[30:36], self.R[36:42], self.R[42:]]
            j = 0
            Bn = [0] * 32
            pos = 0
            while j < 8:
                m = (B[j][0] << 1) + B[j][5]
                n = (B[j][1] << 3) + (B[j][2] << 2) + (B[j][3] << 1) + B[j][4]
                v = des.__sbox[j][(m << 4) + n]
                Bn[pos] = (v & 8) >> 3
                Bn[pos + 1] = (v & 4) >> 2
                Bn[pos + 2] = (v & 2) >> 1
                Bn[pos + 3] = v & 1
                pos += 4
                j += 1

            self.R = self.__permutate(des.__p, Bn)
            self.R = list(map((lambda x, y: x ^ y), self.R, self.L))
            self.L = tempR
            i += 1
            iteration += iteration_adjustment

        self.final = self.__permutate(des.__fp, self.R + self.L)
        return self.final

    def crypt(self, data, crypt_type):
        if not data:
            return ''
        if len(data) % self.block_size != 0:
            if crypt_type == des.DECRYPT:
                raise ValueError('Invalid data length, data must be a multiple of ' + str(self.block_size) + ' bytes\n.')
            if not self.getPadding():
                raise ValueError('Invalid data length, data must be a multiple of ' + str(self.block_size) + ' bytes\n. Try setting the optional padding character')
            else:
                data += (self.block_size - len(data) % self.block_size) * self.getPadding()
        if self.getMode() == CBC:
            if self.getIV():
                iv = self.__String_to_BitList(self.getIV())
            else:
                raise ValueError('For CBC mode, you must supply the Initial Value (IV) for ciphering')
        i = 0
        dict = {}
        result = []
        while i < len(data):
            block = self.__String_to_BitList(data[i:i + 8])
            if self.getMode() == CBC:
                if crypt_type == des.ENCRYPT:
                    block = list(map((lambda x, y: x ^ y), block, iv))
                processed_block = self.__des_crypt(block, crypt_type)
                if crypt_type == des.DECRYPT:
                    processed_block = list(map((lambda x, y: x ^ y), processed_block, iv))
                    iv = block
                else:
                    iv = processed_block
            else:
                processed_block = self.__des_crypt(block, crypt_type)
            result.append(self.__BitList_to_String(processed_block))
            i += 8

        if _pythonMajorVersion < 3:
            return ('').join(result)
        else:
            return bytes.fromhex('').join(result)
        return

    def encrypt(self, data, pad=None, padmode=None):
        data = self._guardAgainstUnicode(data)
        if pad is not None:
            pad = self._guardAgainstUnicode(pad)
        data = self._padData(data, pad, padmode)
        return self.crypt(data, des.ENCRYPT)

    def decrypt(self, data, pad=None, padmode=None):
        data = self._guardAgainstUnicode(data)
        if pad is not None:
            pad = self._guardAgainstUnicode(pad)
        data = self.crypt(data, des.DECRYPT)
        return self._unpadData(data, pad, padmode)


class triple_des(_baseDes):

    def __init__(self, key, mode=ECB, IV=None, pad=None, padmode=PAD_NORMAL):
        _baseDes.__init__(self, mode, IV, pad, padmode)
        self.setKey(key)
        return

    def setKey(self, key):
        self.key_size = 24
        if len(key) != self.key_size:
            if len(key) == 16:
                self.key_size = 16
            else:
                raise ValueError('Invalid triple DES key size. Key must be either 16 or 24 bytes long')
        if self.getMode() == CBC:
            if not self.getIV():
                self.setIV(key[:self.block_size])
            if len(self.getIV()) != self.block_size:
                raise ValueError('Invalid IV, must be 8 bytes in length')
        self.__key1 = des(key[:8], self._mode, self._iv, self._padding, self._padmode)
        self.__key2 = des(key[8:16], self._mode, self._iv, self._padding, self._padmode)
        if self.key_size == 16:
            self.__key3 = self.__key1
        else:
            self.__key3 = des(key[16:], self._mode, self._iv, self._padding, self._padmode)
        _baseDes.setKey(self, key)
        return

    def setMode(self, mode):
        _baseDes.setMode(self, mode)
        for key in (self.__key1, self.__key2, self.__key3):
            key.setMode(mode)

        return

    def setPadding(self, pad):
        _baseDes.setPadding(self, pad)
        for key in (self.__key1, self.__key2, self.__key3):
            key.setPadding(pad)

        return

    def setPadMode(self, mode):
        _baseDes.setPadMode(self, mode)
        for key in (self.__key1, self.__key2, self.__key3):
            key.setPadMode(mode)

        return

    def setIV(self, IV):
        _baseDes.setIV(self, IV)
        for key in (self.__key1, self.__key2, self.__key3):
            key.setIV(IV)

        return

    def encrypt(self, data, pad=None, padmode=None):
        ENCRYPT = des.ENCRYPT
        DECRYPT = des.DECRYPT
        data = self._guardAgainstUnicode(data)
        if pad is not None:
            pad = self._guardAgainstUnicode(pad)
        data = self._padData(data, pad, padmode)
        if self.getMode() == CBC:
            self.__key1.setIV(self.getIV())
            self.__key2.setIV(self.getIV())
            self.__key3.setIV(self.getIV())
            i = 0
            result = []
            while i < len(data):
                block = self.__key1.crypt(data[i:i + 8], ENCRYPT)
                block = self.__key2.crypt(block, DECRYPT)
                block = self.__key3.crypt(block, ENCRYPT)
                self.__key1.setIV(block)
                self.__key2.setIV(block)
                self.__key3.setIV(block)
                result.append(block)
                i += 8

            if _pythonMajorVersion < 3:
                return ('').join(result)
            else:
                return bytes.fromhex('').join(result)
        else:
            data = self.__key1.crypt(data, ENCRYPT)
            data = self.__key2.crypt(data, DECRYPT)
            return self.__key3.crypt(data, ENCRYPT)
        return

    def decrypt(self, data, pad=None, padmode=None):
        ENCRYPT = des.ENCRYPT
        DECRYPT = des.DECRYPT
        data = self._guardAgainstUnicode(data)
        if pad is not None:
            pad = self._guardAgainstUnicode(pad)
        if self.getMode() == CBC:
            self.__key1.setIV(self.getIV())
            self.__key2.setIV(self.getIV())
            self.__key3.setIV(self.getIV())
            i = 0
            result = []
            while i < len(data):
                iv = data[i:i + 8]
                block = self.__key3.crypt(iv, DECRYPT)
                block = self.__key2.crypt(block, ENCRYPT)
                block = self.__key1.crypt(block, DECRYPT)
                self.__key1.setIV(iv)
                self.__key2.setIV(iv)
                self.__key3.setIV(iv)
                result.append(block)
                i += 8

            if _pythonMajorVersion < 3:
                data = ('').join(result)
            else:
                data = bytes.fromhex('').join(result)
        else:
            data = self.__key3.crypt(data, DECRYPT)
            data = self.__key2.crypt(data, ENCRYPT)
            data = self.__key1.crypt(data, DECRYPT)
        return self._unpadData(data, pad, padmode)


