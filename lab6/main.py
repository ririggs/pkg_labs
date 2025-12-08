import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class SolidK:
    def __init__(self):
        k_xy = np.array(
            [
                [0, 0],
                [0, 5],
                [1, 5],
                [1, 3],
                [3, 5],
                [4, 5],
                [2, 2.5],
                [4, 0],
                [3, 0],
                [1, 2],
                [1, 0],
                [1, 0],
            ]
        )

        z_front = 1.0
        z_back = 0.0
        num_points = 12
        self.vertices = np.zeros((num_points * 2, 4))

        for i in range(num_points):
            self.vertices[i] = [k_xy[i][0], k_xy[i][1], z_back, 1]
            self.vertices[i + num_points] = [k_xy[i][0], k_xy[i][1], z_front, 1]

        self.vertices = self.vertices.T

        self.faces = []
        self.faces.append(list(range(num_points)))  
        self.faces.append(list(range(num_points, 2 * num_points)))  

        contour_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0]
        for i in range(len(contour_indices) - 1):
            idx1 = contour_indices[i]
            idx2 = contour_indices[i + 1]
            face = [idx1, idx2, idx2 + num_points, idx1 + num_points]
            self.faces.append(face)

        self.faces.append([3, 9, 9 + num_points, 3 + num_points])

        self.edges = []
        for face in self.faces:
            for i in range(len(face)):
                self.edges.append((face[i], face[(i + 1) % len(face)]))

    def get_translation_matrix(self, dx, dy, dz):
        return np.array([[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]])

    def get_scaling_matrix(self, sx, sy, sz):
        return np.array([[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]])

    def get_rotation_matrix(self, axis, theta_degrees):
        theta = np.radians(theta_degrees)
        axis = np.array(axis) / np.linalg.norm(axis)
        u_x, u_y, u_z = axis
        c, s = np.cos(theta), np.sin(theta)
        t = 1 - c
        return np.array(
            [
                [t * u_x**2 + c, t * u_x * u_y - s * u_z, t * u_x * u_z + s * u_y, 0],
                [t * u_x * u_y + s * u_z, t * u_y**2 + c, t * u_y * u_z - s * u_x, 0],
                [t * u_x * u_z - s * u_y, t * u_y * u_z + s * u_x, t * u_z**2 + c, 0],
                [0, 0, 0, 1],
            ]
        )

    def transform(self, matrix):
        self.vertices = np.dot(matrix, self.vertices)



letter = SolidK()

M_rot_standing = letter.get_rotation_matrix(axis=[1, 0, 0], theta_degrees=90)
M_scale = letter.get_scaling_matrix(1.2, 1.2, 1.2)
M_trans_center = letter.get_translation_matrix(-2, 0.5, 0)
M_total = np.dot(M_trans_center, np.dot(M_rot_standing, M_scale))
letter.transform(M_total)

fig = plt.figure(figsize=(14, 10), layout="constrained")
fig.suptitle('Твердотельная модель буквы "К" (вертикальная) и проекции', fontsize=16)


def plot_letter(ax, vertices, faces, edges, title, p_type="3d"):
    if p_type == "3d":
        poly3d_list = [vertices[0:3, f].T for f in faces]

        collection = Poly3DCollection(
            poly3d_list, facecolor="skyblue", edgecolor="navy", alpha=0.8
        )
        ax.add_collection3d(collection)

        x_lims = [np.min(vertices[0, :]), np.max(vertices[0, :])]
        y_lims = [np.min(vertices[1, :]), np.max(vertices[1, :])]
        z_lims = [np.min(vertices[2, :]), np.max(vertices[2, :])]

        ax.set_xlim(x_lims)
        ax.set_ylim(y_lims)
        ax.set_zlim(z_lims)

        x_range = x_lims[1] - x_lims[0]
        y_range = y_lims[1] - y_lims[0]
        z_range = z_lims[1] - z_lims[0]
        ax.set_box_aspect((x_range, y_range, z_range))

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

    else:
        for edge in edges:
            p1 = vertices[:, edge[0]]
            p2 = vertices[:, edge[1]]
            if "Oxy" in title:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], "k-", lw=1)
            elif "Oxz" in title:
                ax.plot([p1[0], p2[0]], [p1[2], p2[2]], "k-", lw=1)
            elif "Oyz" in title:
                ax.plot([p1[1], p2[1]], [p1[2], p2[2]], "k-", lw=1)

        ax.grid(True)
        ax.set_aspect("equal")

        if "Oxy" in title:
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
        elif "Oxz" in title:
            ax.set_xlabel("X")
            ax.set_ylabel("Z")
        elif "Oyz" in title:
            ax.set_xlabel("Y")
            ax.set_ylabel("Z")

    ax.set_title(title)


ax1 = fig.add_subplot(2, 2, 1, projection="3d")
ax1.view_init(elev=20, azim=-60)
plot_letter(ax1, letter.vertices, letter.faces, letter.edges, "3D Твердотельная модель")

ax2 = fig.add_subplot(2, 2, 2)
plot_letter(
    ax2, letter.vertices, letter.faces, letter.edges, "Проекция Oxy (Вид сверху)", "2d"
)

ax3 = fig.add_subplot(2, 2, 3)
plot_letter(
    ax3, letter.vertices, letter.faces, letter.edges, "Проекция Oxz (Вид спереди)", "2d"
)

ax4 = fig.add_subplot(2, 2, 4)
plot_letter(
    ax4, letter.vertices, letter.faces, letter.edges, "Проекция Oyz (Вид сбоку)", "2d"
)

plt.show()
