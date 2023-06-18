import time


class TimeDifference:
    def __init__(self, num_points=20):
        self.previous_time = time.time()
        self.num_points = num_points
        self.time_points = []

    def update_and_get_difference(self):
        current_time = time.time()
        time_diff = (current_time - self.previous_time) * 1000
        self.previous_time = current_time

        # 更新间隔时间点数列表
        self.time_points.append(time_diff)
        if len(self.time_points) > self.num_points:
            self.time_points.pop(0)

        return time_diff

    def get_average_difference(self):
        if not self.time_points:
            return 0
        return sum(self.time_points) / len(self.time_points)

    def print_time_difference(self):
        diff = self.update_and_get_difference()
        average_diff = self.get_average_difference()

        # 将时间差值四舍五入为整数
        diff_int = round(diff)
        average_diff_int = round(average_diff)

        print(f"两次运行到此处的时间差为：{diff_int}ms，平均时间差为：{average_diff_int}ms")
