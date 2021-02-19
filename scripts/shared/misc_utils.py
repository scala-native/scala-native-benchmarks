def dict_write_arr(kv, arr_key, conf_kvs):
    for index, inner_kv in enumerate(conf_kvs):
        for k, v in inner_kv.items():
            kv['{}.{}.{}'.format(arr_key, index, k)] = v


def dict_get_arr(kv, arr_key):
    arr = []
    arr_kv = {}
    max_index = -1
    for k, v in kv.items():
        if k.startswith(arr_key + '.'):
            _, raw_index, key = k.split('.')
            index = int(raw_index)
            max_index = max(index, max_index)
            arr_kv.get(index, {})[key] = v
    for index in range(max_index + 1):
        arr.append(arr_kv.get(index))

    return arr