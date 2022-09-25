import queue

test = queue.Queue()

test.put(1)
test.put(2)

temp1 = test.get()
temp2 = test.get()

print(temp1, temp2)