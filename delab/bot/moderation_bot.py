import logging

from delab.delab_enums import PLATFORM

logger = logging.getLogger(__name__)


def send_post(intervention_id, platform=PLATFORM.REDDIT):
    logger.debug("send out moderation post {}".format(intervention_id))
    # TODO implement
    pass
