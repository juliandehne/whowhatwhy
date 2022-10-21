from django.db import models


class VERSION(models.TextChoices):
    v001 = "v0.0.1"
    v002 = "v0.0.2"
    v003 = "v0.0.3"  # current
    v004 = "v0.0.4"
    v005 = "v0.0.5"
    v006 = "v0.0.6"


class PLATFORM(models.TextChoices):
    REDDIT = "reddit"
    TWITTER = "twitter"
    DELAB = "delab"


class TWEET_RELATIONSHIPS(models.TextChoices):
    REPLIED_TO = "replied_to"
    RETWEETED = "retweeted"
    QUOTED = "quoted"


class LANGUAGE(models.TextChoices):
    ENGLISH = "en"
    GERMAN = "de"
    POLISH = "pl"
    SPANISH = "es"
    UNKNOWN = "unk"


class Likert(models.IntegerChoices):
    STRONGLY_NOT_AGREE = -2
    NOT_AGREE = -1
    NOT_SURE = 0
    AGREE = 1
    AGREE_STRONGLY = 2


class INTOLERANCE(models.TextChoices):
    RELIGIOUS = "rel"
    SEXUALITY = "sex"
    ETHNICITY = "eth"
    RACISM = "rac"
    BODYSHAMING = "body"
    OTHERGROUPS = "group"
    NONE = "none"


class STRATEGIES(models.TextChoices):
    NORMATIVE = "normative"
    KANTIAN = "kantian"
    EXPERIENCE = "experience"


class NETWORKRELS(models.TextChoices):
    FOLLOWS = "follows"
    mentions = "mentions"


class MODERATION(models.TextChoices):
    ACADEMIC = "academic",
    THERAPEUTIC = "therapeutic",
    DIPLOMATIC, = "diplomatic",
    ARBITRATION = "by arbitration"
    NO_NEED = "no need"

class ORGANISATION(models.TextChoices):
    FRIDAYS_FOR_FUTURE = "fff"
    GREENPEACE = "greenpeace"
    GOVERNMENTAL = "governmental"
    OTHER = "other"







