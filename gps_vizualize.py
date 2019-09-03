import smopy
from matplotlib import pyplot as plt


map = smopy.Map(49.2538, 16.95, 49.3238, 17.4, z=20)
map.show_ipython()
x, y = map.to_pixels(49.2738, 16.997)
ax = map.show_mpl(figsize=(20, 8), dpi=300)
ax.plot(x, y, 'or', ms=10, mew=2)
plt.savefig("mapa.png")
plt.show()
