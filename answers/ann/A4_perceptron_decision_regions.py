import numpy as np
import matplotlib.pyplot as plt

x = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
y = np.array([-1, -1, -1, 1])

w = np.zeros(2)
b = 0

for _ in range(6):
    for i in range(len(x)):
        out = np.sign(np.dot(x[i], w) + b)
        if out != y[i]:
            w = w + 0.3 * y[i] * x[i]
            b = b + 0.3 * y[i]

x1_min, x1_max = x[:, 0].min() - 1, x[:, 0].max() + 1
x2_min, x2_max = x[:, 1].min() - 1, x[:, 1].max() + 1

xx, yy = np.meshgrid(np.arange(x1_min, x1_max, 0.01),
                     np.arange(x2_min, x2_max, 0.01))

z = np.sign(np.dot(np.c_[xx.ravel(), yy.ravel()], w) + b)
z = z.reshape(xx.shape)

plt.contourf(xx, yy, z, alpha=0.8)
plt.scatter(x[:, 0], x[:, 1], c=y)

plt.xlabel("x1")
plt.ylabel("x2")
plt.title("Perceptron Decision Regions")

plt.show()
