import datetime
import random
from typing import List


class TimerUtils:

    @staticmethod
    def random_scheduler(num_executions: int = 1,
                         begin_hour: int = 7,
                         end_hour: int = 23,
                         min_interval: int = 20,
                         max_interval: int = 40) -> List[datetime.datetime]:
        """
        按执行次数生成随机定时器
        :param num_executions: 执行次数
        :param begin_hour: 开始时间
        :param end_hour: 结束时间
        :param min_interval: 最小间隔分钟
        :param max_interval: 最大间隔分钟
        """
        trigger: list = []
        # 当前时间
        now = datetime.datetime.now()
        # 创建随机的时间触发器
        random_trigger = now.replace(hour=begin_hour, minute=0, second=0, microsecond=0)
        for _ in range(num_executions):
            # 随机生成下一个任务的时间间隔
            interval_minutes = random.randint(min_interval, max_interval)
            random_interval = datetime.timedelta(minutes=interval_minutes)
            # 更新当前时间为下一个任务的时间触发器
            random_trigger += random_interval
            # 达到结束时间时退出
            if random_trigger.hour > end_hour:
                break
            # 添加到队列
            trigger.append(random_trigger)

        return trigger

    from datetime import datetime, timedelta

    @staticmethod
    def time_difference(input_datetime: datetime) -> str:
        """
        判断输入时间与当前的时间差，如果输入时间大于当前时间则返回时间差，否则返回空字符串
        """
        if not input_datetime:
            return ""
        current_datetime = datetime.datetime.now(datetime.timezone.utc).astimezone()
        time_difference = input_datetime - current_datetime

        if time_difference.total_seconds() < 0:
            return ""

        days = time_difference.days
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        time_difference_string = ""
        if days > 0:
            time_difference_string += f"{days}天"
        if hours > 0:
            time_difference_string += f"{hours}小时"
        if minutes > 0:
            time_difference_string += f"{minutes}分钟"

        return time_difference_string
