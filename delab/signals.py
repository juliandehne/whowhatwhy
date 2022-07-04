import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.dispatch import receiver
from django.utils import timezone

from delab.bot.intolerance_bot import generate_answers
from delab.bot.intolerance_bot import send_message
from delab.bot.sender import publish_moderation
from delab.models import SimpleRequest, Tweet, TWIntoleranceRating, IntoleranceAnswer, \
    IntoleranceAnswerValidation
from delab.delab_enums import PLATFORM
from delab.tasks import download_conversations_scheduler
from django_project.settings import min_intolerance_coders_needed, min_intolerance_answer_coders_needed

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tweet)
def process_moderation(sender, instance, created, **kwargs):
    if instance.platform == PLATFORM.DELAB and instance.publish and created:
        publish_moderation(instance)


@receiver(post_save, sender=TWIntoleranceRating)
def process_labeled_intolerant_tweets(sender, instance: TWIntoleranceRating, created, **kwargs):
    """
    If it is the second time the tweet was rated as intolerant by different users, and if there has not been
    generated answers for the intolerance experiment and the tweet was seen as interpretable from the context
    and the intolerance was directed versus a group and not a person, in this case the answer is generated
    in the db table and will be presented as a candidate to be sent to social media after validation.
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        ratings_count = TWIntoleranceRating.objects.filter(candidate=instance.candidate,
                                                           u_intolerance_rating=2,
                                                           u_clearness_rating=2,
                                                           u_person_hate=False).count()
        exists_previous_labeling = ratings_count >= min_intolerance_coders_needed
        if exists_previous_labeling:
            # filter if the candidate has already a generated answer
            already_exists_answer = IntoleranceAnswer.objects.filter(candidate=instance.candidate).exists()
            # filter if the candidate belongs to a discussion where an intervention has taken place already
            already_sent_answer_in_discussion = IntoleranceAnswer.objects.filter(
                candidate__tweet__conversation_id=instance.candidate.tweet.conversation_id).filter(
                twitter_id__isnull=False).exists()
            if not already_exists_answer and not already_sent_answer_in_discussion:
                answer1, answer2, answer3 = generate_answers(instance.candidate)
                IntoleranceAnswer.objects.create(
                    answer1=answer1,
                    answer2=answer2,
                    answer3=answer3,
                    candidate=instance.candidate,
                )
                logger.info("answer for intolerance candidate {} was created in db".format(instance.candidate.pk))


@receiver(post_save, sender=IntoleranceAnswerValidation)
def process_validated_answers(sender, instance: IntoleranceAnswerValidation, created, **kwargs):
    """
    This will send the tweet out with the answer if the validation is successful
    :return:
    """
    enough_validations = instance.answer.intoleranceanswervalidation_set.filter(
        valid=True).count() >= min_intolerance_answer_coders_needed
    if enough_validations:
        logger.info("sending out answer tweet with answer {} (needs implementation)".format("some strat"))
        send_message(instance.answer.candidate)


@receiver(post_save, sender=SimpleRequest)
def process_simple_request(sender, instance, created, **kwargs):
    """ After entering the hashtags on the website the query is persisted. Afterwards a twitter call is started to
    download a random conversation.

        Keyword arguments:
        instance -- the title string with space seperated hashtags
    """
    logging.info("received signal from post_save {} for pk {}".format(timezone.now(), instance.pk))

    scripted_topics = ["moderation_mining_2", "TopicNotGiven"]
    if created and instance.topic.title not in scripted_topics:
        # cleaned_hashtags = convert_request_to_hashtag_list(instance.title)
        download_conversations_scheduler(instance.topic.title,
                                         instance.platform,
                                         instance.title,
                                         simple_request_id=instance.pk,
                                         verbose_name="simple_request_{}".format(instance.pk),
                                         schedule=timezone.now(),
                                         simulate=False, max_data=instance.max_data,
                                         fast_mode=instance.fast_mode, language=instance.language)
