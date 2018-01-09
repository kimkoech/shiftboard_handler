import functools

my_list = [1, 1, 1, 1, 1, 1]


def compare(x, y):
    if x == y:
        print(x)
    else:
        print(False)


functools.reduce(compare, my_list)

# this one works

lis = [3, 5, 7, 9, 0, 2, 3, 5, 7, 8, 1, 3, 5]

timeindices = []
i = 0
for x, y in zip(lis, lis[1:]):
    plus_one_mode_of_x = (x + 1) % 10
    if plus_one_mode_of_x == y:
        timeindices.append(i)
    else:
        i += 1

print(timeindices)


# function that adds time duplicates to innerTime list
def create_time_duplicate(time_list, indices_list):
    new_list = time_list
    store_times = []
    for index in indices_list:
        # find time and store
        store_times.append(new_list[index])
    # because indices will change, find new indices and duplicate
    for _time in store_times:
        new_index = new_list.index(_time)
        # insert duplicate at index
        new_list.insert(new_index, _time)
    # return final list
    return new_list


time_list_list = [['10am', '11am'], ['11am', '12pm'], ['12pm', '1pm'], ['1pm', '2pm'], ['2pm', '3pm'], ['3pm', '5pm'], ['3pm', '6pm'], ['5pm', '7pm'], ['6pm', '8pm'], ['7pm', '10pm'], ['8pm', '10pm']]

indices_list_list = [2, 4]

print(create_time_duplicate(time_list_list, indices_list_list))
