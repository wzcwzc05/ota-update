import copy

# lst_1 = [1, 2, [1, 2, 3], 4]
# lst_2 = lst_1
# lst_3 = copy.copy(lst_1)
# lst_4 = copy.deepcopy(lst_1)

# print(id(lst_1), id(lst_2), id(lst_3), id(lst_4))

# lst_1[2].append(100)
# print(lst_1, lst_2, lst_3, lst_4)

a = [1, 2, 3, [5, 6]]
b = a+[7]
print(id(a) == id(b))
a[0] = -1
a[3][0] = -1
print(a)
print(b)
