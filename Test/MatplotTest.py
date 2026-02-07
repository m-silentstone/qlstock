import matplotlib.pyplot as plt
import numpy as np

data = {'a': np.arange(50),
        'c': np.random.randint(0, 50, 50),
        'd': np.random.randn(50)}
data['b'] = data['a'] + 10 * np.random.randn(50)
data['d'] = np.abs(data['d']) * 100
# 散点图  参数：x轴数据，y轴数据，点大小s，点颜色c
plt.scatter('a', 'b', s='d', c='c', data=data)
plt.xlabel('entry a')
plt.ylabel('entry b')
plt.show()