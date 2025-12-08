import math
import time

from main import RasterizationApp


class PerformanceTester:
    def __init__(self):
        self.results = []

    def step_by_step_algorithm(self, x1, y1, x2, y2):
        """Пошаговый алгоритм"""
        pixels = []
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x1, y1)]

        x_inc = dx / steps
        y_inc = dy / steps
        x = x1
        y = y1

        for _ in range(steps + 1):
            pixels.append((round(x), round(y)))
            x += x_inc
            y += y_inc

        return pixels

    def dda_algorithm(self, x1, y1, x2, y2):
        """Алгоритм ЦДА"""
        pixels = []
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x1, y1)]

        x_inc = dx / steps
        y_inc = dy / steps
        x = float(x1)
        y = float(y1)

        for _ in range(steps + 1):
            pixels.append((round(x), round(y)))
            x += x_inc
            y += y_inc

        return pixels

    def bresenham_line_algorithm(self, x1, y1, x2, y2):
        """Алгоритм Брезенхема для отрезков"""
        pixels = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x = x1
        y = y1
        x_sign = 1 if x2 > x1 else -1
        y_sign = 1 if y2 > y1 else -1

        if dx > dy:
            error = dx / 2
            while x != x2:
                pixels.append((x, y))
                error -= dy
                if error < 0:
                    y += y_sign
                    error += dx
                x += x_sign
            pixels.append((x, y))
        else:
            error = dy / 2
            while y != y2:
                pixels.append((x, y))
                error -= dx
                if error < 0:
                    x += x_sign
                    error += dy
                y += y_sign
            pixels.append((x, y))

        return pixels

    def bresenham_circle_algorithm(self, cx, cy, radius):
        """Алгоритм Брезенхема для окружности"""
        pixels = []
        x = 0
        y = radius
        d = 3 - 2 * radius

        def add_circle_points(cx, cy, x, y):
            return [
                (cx + x, cy + y),
                (cx - x, cy + y),
                (cx + x, cy - y),
                (cx - x, cy - y),
                (cx + y, cy + x),
                (cx - y, cy + x),
                (cx + y, cy - x),
                (cx - y, cy - x),
            ]

        while x <= y:
            pixels.extend(add_circle_points(cx, cy, x, y))
            if d < 0:
                d = d + 4 * x + 6
            else:
                d = d + 4 * (x - y) + 10
                y -= 1
            x += 1

        return pixels

    def test_line_algorithm(self, name, algorithm, test_cases, iterations=1000):
        """Тестирование алгоритма отрезка"""
        print(f"\n{'=' * 60}")
        print(f"Тестирование: {name}")
        print(f"{'=' * 60}")

        for test_name, (x1, y1, x2, y2) in test_cases.items():
            times = []

            for _ in range(iterations):
                start = time.perf_counter()
                pixels = algorithm(x1, y1, x2, y2)
                end = time.perf_counter()
                times.append((end - start) * 1_000_000)  # в микросекундах

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            pixel_count = len(pixels)

            print(f"\nТест: {test_name}")
            print(f"  Координаты: ({x1}, {y1}) -> ({x2}, {y2})")
            print(f"  Количество пикселей: {pixel_count}")
            print(f"  Среднее время: {avg_time:.3f} мкс")
            print(f"  Минимальное время: {min_time:.3f} мкс")
            print(f"  Максимальное время: {max_time:.3f} мкс")

            self.results.append(
                {
                    "algorithm": name,
                    "test": test_name,
                    "pixels": pixel_count,
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                }
            )

    def test_circle_algorithm(self, iterations=1000):
        """Тестирование алгоритма окружности"""
        print(f"\n{'=' * 60}")
        print(f"Тестирование: Алгоритм Брезенхема (окружность)")
        print(f"{'=' * 60}")

        test_cases = {
            "Малая окружность": (0, 0, 5),
            "Средняя окружность": (0, 0, 20),
            "Большая окружность": (0, 0, 50),
            "Очень большая окружность": (0, 0, 100),
        }

        for test_name, (cx, cy, radius) in test_cases.items():
            times = []

            for _ in range(iterations):
                start = time.perf_counter()
                pixels = self.bresenham_circle_algorithm(cx, cy, radius)
                end = time.perf_counter()
                times.append((end - start) * 1_000_000)

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            pixel_count = len(pixels)

            print(f"\nТест: {test_name}")
            print(f"  Центр: ({cx}, {cy}), Радиус: {radius}")
            print(f"  Количество пикселей: {pixel_count}")
            print(f"  Среднее время: {avg_time:.3f} мкс")
            print(f"  Минимальное время: {min_time:.3f} мкс")
            print(f"  Максимальное время: {max_time:.3f} мкс")

            self.results.append(
                {
                    "algorithm": "Брезенхем (окружность)",
                    "test": test_name,
                    "pixels": pixel_count,
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                }
            )

    def run_all_tests(self):
        """Запуск всех тестов"""
        # Тестовые случаи для отрезков
        test_cases = {
            "Горизонтальная линия": (0, 0, 50, 0),
            "Вертикальная линия": (0, 0, 0, 50),
            "Диагональ 45°": (0, 0, 50, 50),
            "Наклонная линия": (0, 0, 50, 25),
            "Длинная линия": (0, 0, 100, 50),
        }

        # Тестирование всех алгоритмов отрезков
        self.test_line_algorithm(
            "Пошаговый алгоритм", self.step_by_step_algorithm, test_cases
        )

        self.test_line_algorithm("Алгоритм ЦДА", self.dda_algorithm, test_cases)

        self.test_line_algorithm(
            "Алгоритм Брезенхема (отрезки)", self.bresenham_line_algorithm, test_cases
        )

        # Тестирование алгоритма окружности
        self.test_circle_algorithm()

        # Вывод сводной таблицы
        self.print_summary()

    def print_summary(self):
        """Вывод сводной таблицы результатов"""
        print(f"\n{'=' * 80}")
        print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
        print(f"{'=' * 80}")

        # Группировка по тестам
        tests = {}
        for result in self.results:
            test = result["test"]
            if test not in tests:
                tests[test] = []
            tests[test].append(result)

        for test_name, results in tests.items():
            print(f"\n{test_name}:")
            print(f"{'Алгоритм':<35} {'Пиксели':<12} {'Время (мкс)':<15}")
            print("-" * 62)

            for r in results:
                print(f"{r['algorithm']:<35} {r['pixels']:<12} {r['avg_time']:>10.3f}")

        # Сравнение алгоритмов отрезков на одном тесте
        print(f"\n{'=' * 80}")
        print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ АЛГОРИТМОВ ОТРЕЗКОВ")
        print(f"{'=' * 80}")

        line_algorithms = [
            "Пошаговый алгоритм",
            "Алгоритм ЦДА",
            "Алгоритм Брезенхема (отрезки)",
        ]
        test_case = "Диагональ 45°"

        print(f"\nТестовый случай: {test_case}")
        print(f"{'Алгоритм':<35} {'Время (мкс)':<15} {'Относительная скорость'}")
        print("-" * 70)

        base_results = [
            r
            for r in self.results
            if r["test"] == test_case and r["algorithm"] in line_algorithms
        ]

        if base_results:
            fastest = min(base_results, key=lambda x: x["avg_time"])

            for r in base_results:
                relative = r["avg_time"] / fastest["avg_time"]
                print(
                    f"{r['algorithm']:<35} {r['avg_time']:>10.3f}      {relative:>6.2f}x"
                )


def main():
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ АЛГОРИТМОВ РАСТЕРИЗАЦИИ")
    print("=" * 80)
    print("\nДанный скрипт выполняет серию тестов для измерения производительности")
    print("всех реализованных алгоритмов растеризации.")
    print(
        "\nКаждый тест выполняется 1000 раз для получения статистически значимых результатов."
    )
    print("\nПожалуйста, подождите...\n")

    tester = PerformanceTester()
    tester.run_all_tests()

    print("\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 80)
    print("\nДанные результаты можно использовать в отчете для сравнения")
    print("временных характеристик реализованных алгоритмов.")


if __name__ == "__main__":
    main()
