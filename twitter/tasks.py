from background_task import background

from delab.download_conversations import download_conversations


# this schedules longer running tasks that are regularly polled by the process task that is started in the background
@background(schedule=60)
def download_conversations_scheduler(topic, hashtags):
    download_conversations(topic, hashtags)
