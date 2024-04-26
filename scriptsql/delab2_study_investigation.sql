SELECT
    dt.*,
    cf.*,
    msc.*,
    msi.*,
    'Is this a conversation that can be understood by most people?' AS is_conversation_0_help_text,
    'Is there a specific topic or issue being discussed?' AS is_conversation_1_help_text,
    'Are there different viewpoints or perspectives being presented?' AS is_conversation_2_help_text,
    'Are participants actively questioning or challenging each other''s ideas?' AS is_conversation_3_help_text,
    'Is this a political debate? If unsure mark no.' AS is_conversation_4_help_text,
    'Are there arguments or counterarguments being presented?' AS is_conversation_5_help_text,
    'Are the discussants staying on topic?' AS agenda_control_1_help_text,
    'Is it hard to keep track of the issue at hand?' AS agenda_control_2_help_text,
    'Is the conversation split in two or more very separate topics?' AS agenda_control_3_help_text,
    'Are the discussants showing emotions towards each other?' AS emotion_control_1_help_text,
    'Is someone being attacked or insulted?' AS emotion_control_2_help_text,
    'Is bad language used?' AS emotion_control_3_help_text,
    'Are there many different perspectives (allowed)?' AS participation_1_help_text,
    'Is the discussion dominated by a certain group?' AS participation_2_help_text,
    'Is this a discussion where everyone can join in?' AS participation_3_help_text,
    'Is the discussion very polarized?' AS consensus_seeking_1_help_text,
    'Are the discussants agreeing on things?' AS consensus_seeking_2_help_text,
    'Are they talking past each other?' AS consensus_seeking_3_help_text,
    'Are there some intolerant speech acts in the conversation?' AS norm_control_1_help_text,
    'Are the discussants violating some basic social rules?' AS norm_control_2_help_text,
    'Are there comments that are racist, sexist, antisemitic or similar?' AS norm_control_3_help_text,
    'Are arguments well formulated and understandable?' AS elaboration_support_1_help_text,
    'Are there hidden assumptions that shape the discussion?' AS elaboration_support_2_help_text,
    'Is there a tabu involved (elefant in the room) that needs to be addressed to further the conversation?' AS elaboration_support_3_help_text,
    'Mark this, if the conversation is correct in a technical sense (no weird letters, deleted posts or similar!' AS is_valid_conversation_help_text,
    'The type of moderation strategy needed' AS needs_moderation_help_text
FROM
    delab_tweet dt
INNER JOIN
    delab_conversationflow_tweets dct
    ON dt.id = dct.tweet_id
INNER JOIN
    delab_conversationflow cf
    ON dct.conversationflow_id = cf.id
INNER JOIN
    mt_study_classification msc
    ON cf.id = msc.flow_id
LEFT JOIN
    mt_study_intervention msi
    ON cf.id = msi.flow_id;
