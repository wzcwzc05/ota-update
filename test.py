class clist:
    __lst = [1, 2, 3, 4, 5]

    def remove_k(self, i, k):
        for j in range(i+k, len(self.__lst)):
            self.__lst[j-k] = self.__lst[j]
        self.__lst = self.__lst[:-k]


if __name__ == "__main__":
    a = clist()
    a.remove_k(1, 2)
