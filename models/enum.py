from enum import Enum

class BaseEnum(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @property
    def display(self):
        return self.label

    @classmethod
    def get_value_by_label(cls, label):
        return next((member.value for member in cls if member.label == label), None)

    @classmethod
    def get_enum_by_label(cls, label):
        return next((member for member in cls if member.label == label), None)

    @classmethod
    def display_of(cls, value):
        try:
            if value is None:
                return ""
            return cls(value).display
        except ValueError:
            return str(value)

    @classmethod
    def choices(cls):
        return [(member.value, member.label) for member in cls]

#  数据分类枚举
class DataType(BaseEnum):
    TEXT = 1, '文本'
    IMAGE = 2, '图片' 
    AUDIO = 3, '音频'
    VIDEO = 4, '视频'

# 题型枚举
class QuestionType(BaseEnum):
    MULTIPLE_CHOICE = 1, '选择题'
    TRUE_FALSE = 2, '判断题'
    QA = 3, '问答题'

# 标签枚举
class QuestionLabel(BaseEnum):
    MATH = 1, '数学'
    READING = 2, '文字理解'
    RAG = 3, 'RAG召回'

# 模型类型枚举
class ModelType(BaseEnum):
    REMOTE_MODEL = 1, '远程模型'
    LOCAL_MODEL = 2, '本地模型'

# 配置类型枚举
class ConfigType(BaseEnum):
    TEST_MODEL = 1, '被测模型'
    REFEREE_MODEL = 2, '裁判模型'

# 是否流式枚举
class IsStream(BaseEnum):
    NO = 0, '否'
    YES = 1, '是'
