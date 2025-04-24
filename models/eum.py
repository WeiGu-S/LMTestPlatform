from enum import Enum

#  数据类型枚举
class DataType(int, Enum):
    TEXT = 1, '文本'
    IMAGE = 2, '图片' 
    AUDIO = 3, '音频'
    VIDEO = 4, '视频'

    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @property
    def display(self):
        return self.label

# 题目类型枚举
class QuestionType(int, Enum):
    MULTIPLE_CHOICE = 1, '选择题'
    TRUE_FALSE = 2, '判断题'
    QA = 3, '问答题'

    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @property 
    def display(self):
        return self.label

# 能力类型枚举
class QuestionLabel(int, Enum):
    MATH = 1, '数学'
    READING = 2, '文字理解'
    RAG = 3, 'RAG召回'

    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @property
    def display(self):
        return self.label
