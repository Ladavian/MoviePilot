import inspect
from types import FunctionType
from typing import Any, Callable


class ObjectUtils:

    @staticmethod
    def is_obj(obj: Any):
        if isinstance(obj, list) \
                or isinstance(obj, dict):
            return True
        elif isinstance(obj, str) \
                or isinstance(obj, int) \
                or isinstance(obj, float) \
                or isinstance(obj, bool) \
                or isinstance(obj, bytes):
            return False
        else:
            return str(obj).startswith("{") \
                or str(obj).startswith("[")

    @staticmethod
    def arguments(func: Callable) -> int:
        """
        返回函数的参数个数
        """
        signature = inspect.signature(func)
        parameters = signature.parameters

        return len(list(parameters.keys()))

    @staticmethod
    def check_method(func: FunctionType) -> bool:
        """
        检查函数是否已实现
        """
        return func.__code__.co_code != b'd\x01S\x00'

    @staticmethod
    def check_signature(func: FunctionType, *args) -> bool:
        """
        检查输出与函数的参数类型是否一致
        """
        # 获取函数的参数信息
        signature = inspect.signature(func)
        parameters = signature.parameters

        # 检查输入参数个数和类型是否一致
        if len(args) != len(parameters):
            return False
        for arg, param in zip(args, parameters.values()):
            if not isinstance(arg, param.annotation):
                return False
        return True
