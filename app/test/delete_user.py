def is_function(array):
    dicts_result = {}

    for elem in array:
        dicts_result[elem[0]] = elem[1]

    return len(dicts_result) == len(array)

print(is_function([(1, 2), (2, 2), (3, 2), (4, 2)]))

