import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(6, 8))
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.8, 1.8)
ax.axis('off')  # Hide the axis

# Draw the base of the laptop
laptop_base = patches.Rectangle((-0.75, -1.2), 1.5, 0.2, color="black")
ax.add_patch(laptop_base)

# Draw the screen of the laptop
laptop_screen = patches.Rectangle((-0.75, -0.4), 1.5, 1.8, edgecolor="black", facecolor="white", lw=3)
ax.add_patch(laptop_screen)

# Draw floating squares to represent creativity
floating_squares = [
    (-0.1, 0.4, 0.24),
    (-0.5, 0.1, 0.18),
    (0.2, 0.15, 0.12),
    (0.5, -0.3, 0.09),
    (-0.6, -0.35, 0.06)
]
for x, y, size in floating_squares:
    square = patches.Rectangle((x, y), size, size, color="black")
    ax.add_patch(square)

# Add project title and slogan as text
#plt.text(0, -1.6, "Automated Tool To Assist Programmers", ha="center", va="center", fontsize=18, fontweight="bold")
#plt.text(0, -1.75, "Declare Variables Instead of War", ha="center", va="center", fontsize=14, color="grey")

# Save and show the plot
plt.savefig("static/images/logo.png", format="png", bbox_inches='tight', pad_inches=0)
plt.show()
