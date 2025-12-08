import copy

import matplotlib.patches as patches
import matplotlib.pyplot as plt

def create_sample_file(filename="input.txt"):
    """Создает тестовый файл с данными, если его нет."""
    content = """5
10 10 90 80
20 90 80 20
-10 50 110 50
50 -10 50 110
30 30 70 70
20 20 80 80
"""
    with open(filename, "w") as f:
        f.write(content)
    print(f"Файл {filename} создан для примера.")


def read_data(filename="input.txt"):
    lines_data = []
    window = []

    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            n = int(lines[0].strip())

            for i in range(1, n + 1):
                coords = list(map(float, lines[i].strip().split()))
                lines_data.append(coords)  # [x1, y1, x2, y2]

            window = list(map(float, lines[n + 1].strip().split()))

    except FileNotFoundError:
        print("Файл не найден. Создаю пример...")
        create_sample_file()
        return read_data(filename)
    except Exception as e:
        print(f"Ошибка чтении файла: {e}")
        return [], []

    return lines_data, window


def liang_barsky(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    """
    Возвращает координаты (nx1, ny1, nx2, ny2) видимой части отрезка
    или None, если отрезок полностью невидим.
    """
    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]

    u1 = 0.0
    u2 = 1.0

    for i in range(4):
        if p[i] == 0:  
            if q[i] < 0:  
                return None
        else:
            t = q[i] / p[i]
            if p[i] < 0: 
                u1 = max(u1, t)
            else:  
                u2 = min(u2, t)

    if u1 > u2:
        return None

    nx1 = x1 + u1 * dx
    ny1 = y1 + u1 * dy
    nx2 = x1 + u2 * dx
    ny2 = y1 + u2 * dy

    return (nx1, ny1, nx2, ny2)


def sutherland_hodgman(subject_polygon, clip_rect):
    """
    subject_polygon: список точек [(x,y), (x,y)...]
    clip_rect: [xmin, ymin, xmax, ymax]
    """
    xmin, ymin, xmax, ymax = clip_rect

    def inside(p, edge):
        x, y = p
        if edge == "left":
            return x >= xmin
        elif edge == "right":
            return x <= xmax
        elif edge == "bottom":
            return y >= ymin
        elif edge == "top":
            return y <= ymax

    def intersect(p1, p2, edge):
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1

        if dx == 0 and dy == 0:
            return p1

        if edge == "left":
            return (xmin, y1 + (xmin - x1) * dy / dx)
        elif edge == "right":
            return (xmax, y1 + (xmax - x1) * dy / dx)
        elif edge == "bottom":
            return (x1 + (ymin - y1) * dx / dy, ymin)
        elif edge == "top":
            return (x1 + (ymax - y1) * dx / dy, ymax)

    output_list = copy.deepcopy(subject_polygon)

    for edge in ["left", "right", "bottom", "top"]:
        input_list = output_list
        output_list = []

        if not input_list:
            break

        s = input_list[-1]

        for e in input_list:
            if inside(e, edge):
                if not inside(s, edge):
                    output_list.append(intersect(s, e, edge))
                output_list.append(e)
            elif inside(s, edge):
                output_list.append(intersect(s, e, edge))
            s = e

    return output_list


def plot_results(lines_data, window, polygon_data=None):
    xmin, ymin, xmax, ymax = window

    rows = 1 if polygon_data is None else 2
    fig, axes = plt.subplots(1, rows, figsize=(4 * rows, 3))
    if rows == 1:
        axes = [axes]

    ax = axes[0]
    ax.set_title("Часть 1: Алгоритм Лианга-Барски (Отрезки)")

    rect = patches.Rectangle(
        (xmin, ymin),
        xmax - xmin,
        ymax - ymin,
        linewidth=2,
        edgecolor="blue",
        facecolor="none",
        label="Окно",
    )
    ax.add_patch(rect)

    for line in lines_data:
        x1, y1, x2, y2 = line
        ax.plot([x1, x2], [y1, y2], color="red", linestyle="--", alpha=0.5, linewidth=1)

        clipped = liang_barsky(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            ax.plot([cx1, cx2], [cy1, cy2], color="green", linewidth=3)

    ax.grid(True)
    ax.legend(["Окно", "Исходные", "Видимые"])
    margin = 20
    ax.set_xlim(xmin - margin, xmax + margin)
    ax.set_ylim(ymin - margin, ymax + margin)

    if polygon_data:
        ax2 = axes[1]
        ax2.set_title("Часть 2: Алгоритм Сазерленда-Ходжмана (Многоугольник)")

        rect2 = patches.Rectangle(
            (xmin, ymin),
            xmax - xmin,
            ymax - ymin,
            linewidth=2,
            edgecolor="blue",
            facecolor="none",
        )
        ax2.add_patch(rect2)

        poly_x = [p[0] for p in polygon_data] + [polygon_data[0][0]]
        poly_y = [p[1] for p in polygon_data] + [polygon_data[0][1]]
        ax2.plot(poly_x, poly_y, color="red", linestyle="--", label="Исходный")

        clipped_poly = sutherland_hodgman(polygon_data, window)

        if len(clipped_poly) > 0:
            c_poly_x = [p[0] for p in clipped_poly] + [clipped_poly[0][0]]
            c_poly_y = [p[1] for p in clipped_poly] + [clipped_poly[0][1]]

            polygon_patch = patches.Polygon(
                clipped_poly,
                closed=True,
                facecolor="green",
                alpha=0.3,
                edgecolor="green",
                linewidth=2,
                label="Видимый",
            )
            ax2.add_patch(polygon_patch)

        ax2.grid(True)
        ax2.legend()
        ax2.set_xlim(xmin - margin, xmax + margin)
        ax2.set_ylim(ymin - margin, ymax + margin)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    segments, window = read_data()

    sample_polygon = [
        (window[0] - 10, window[1] + (window[3] - window[1]) / 2),  
        (window[0] + (window[2] - window[0]) / 2, window[3] + 10),  
        (window[2] + 10, window[1] + (window[3] - window[1]) / 2),  
        (window[0] + (window[2] - window[0]) / 2, window[1] - 10),  
    ]

    if segments and window:
        print(f"Окно отсечения: {window}")
        print(f"Количество отрезков: {len(segments)}")
        plot_results(segments, window, sample_polygon)
    else:
        print("Ошибка данных.")
