import psutil

print('cpu count: {}'.format(psutil.cpu_count()))
for x in range(10):
    print('cpu percent: {}'.format(psutil.cpu_percent(0.3) < 10))
