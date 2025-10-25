class interMessage(object):
    def __init__(self, target, task=None, topic=None, content=None, contentType=None, channel=None, value=None, timestamp=None):
        self.target = target
        self.task = task
        self.topic = topic
        self.contentType = contentType
        self.content = content
        self.channel = channel
        self.value = value
        self.timestamp = timestamp
        self.contentList = []
