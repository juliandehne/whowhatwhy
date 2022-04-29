import copy
import logging

from django.db.models.signals import post_save
# from django.dispatch import receiver
from django.utils import timezone
from django.dispatch import receiver

from delab.bot.intolerance_bot import generate_answers
from delab.models import SimpleRequest, Tweet, TWCandidate, PLATFORM, TWIntoleranceRating, IntoleranceAnswer, \
    IntoleranceAnswerValidation
from django.db.models.signals import post_save
from delab.tasks import download_conversations_scheduler
from delab.bot.sender import publish_moderation
from django_project.settings import min_intolerance_coders_needed, min_intolerance_answer_coders_needed

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tweet)
def process_moderation(sender, instance, created, **kwargs):
    if instance.platform == PLATFORM.DELAB and instance.publish:
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
    exists_previous_labeling = True
    ratings_count = TWIntoleranceRating.objects.filter(candidate=instance.candidate,
                                                       u_intolerance_rating=2,
                                                       u_clearness_rating=2,
                                                       u_person_hate=False).count()
    exists_previous_labeling = ratings_count >= min_intolerance_coders_needed
    if exists_previous_labeling:
        already_exists_answer = IntoleranceAnswer.objects.filter(candidate=instance.candidate).exists()
        if not already_exists_answer:
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
    enough_validations = instance.answer.intoleranceanswervalidation_set.count() >= min_intolerance_answer_coders_needed
    if enough_validations:
        logger.info("sending out answer tweet with answer {} (needs implementation)".format("some strat"))


@receiver(post_save, sender=SimpleRequest)
def process_simple_request(sender, instance, created, **kwargs):
    """ After entering the hashtags on the website the query is persisted. Afterwards a twitter call is started to
    download a random conversation.

        Keyword arguments:
        instance -- the title string with space seperated hashtags
    """
    logging.info("received signal from post_save {} for pk {}".format(timezone.now(), instance.pk))

    if created:
        # cleaned_hashtags = convert_request_to_hashtag_list(instance.title)
        download_conversations_scheduler(instance.topic.title,
                                         instance.platform,
                                         instance.title,
                                         simple_request_id=instance.pk,
                                         verbose_name="simple_request_{}".format(instance.pk),
                                         schedule=timezone.now(),
                                         simulate=False, max_data=instance.max_data,
                                         fast_mode=instance.fast_mode, language=instance.language)


def convert_request_to_hashtag_list(title):
    """ description

        Parameters
        ----------
        title : str
            i.e. "#covid #vaccination"
        Returns
        -------
        [str]
            i.e. [covid, vaccination]
    """
    cleaned_hashtags = []
    if ' ' in title:
        hashtags = title.split(" ")
        for hashtag in hashtags:
            cleaned_hashtags.append(hashtag[1:])  # removes the # symbol
    else:
        cleaned_hashtags.append(title[1:])

    return cleaned_hashtags
