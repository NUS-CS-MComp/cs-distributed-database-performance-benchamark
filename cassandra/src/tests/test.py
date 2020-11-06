#!/usr/bin/env python3
from multiprocessing.pool import ThreadPool

def k():
    num_items = 10

    a = [11] * num_items
    l = [0] * num_items

    def handle_item(i):
        l[i] = i * 2
        print(i, a[i], l[i])

    pool = ThreadPool(8)
    pool.map(handle_item, range(num_items))
    pool.close()

print("test")

k()
