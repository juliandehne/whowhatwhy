SELECT
    au.id,
    au.email,
    au.username,
    up.iban,
    up.full_name,
    COUNT(DISTINCT mc.id) AS classification_count,
    COUNT(DISTINCT mi_as_coder.id) AS intervention_count_as_coder,
    COUNT(DISTINCT mi_as_sendable.id) AS intervention_count_as_sendable,
    (COUNT(DISTINCT mc.id) * 0.08 + COUNT(DISTINCT mi_as_coder.id) * 0.1 + COUNT(DISTINCT mi_as_sendable.id) * 0.1) AS hours,
    ((COUNT(DISTINCT mc.id) * 0.08 + COUNT(DISTINCT mi_as_coder.id) * 0.1 + COUNT(DISTINCT mi_as_sendable.id) * 0.1) * 12) AS payoffs
FROM
    auth_user au
INNER JOIN users_profile up ON au.id = up.user_id
LEFT JOIN mt_study_classification mc ON au.id = mc.coder_id
LEFT JOIN mt_study_intervention mi_as_coder ON au.id = mi_as_coder.coder_id
LEFT JOIN mt_study_intervention mi_as_sendable ON au.id = mi_as_sendable.sendable_coder_id
WHERE
    up.iban IS NOT NULL AND up.iban != ''
GROUP BY
    au.id, au.email, au.username, up.iban, up.full_name;
