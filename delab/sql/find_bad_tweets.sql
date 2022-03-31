select language,text from delab_tweet where to_tsvector(text) @@ to_tsquery('beaner | chinc | chink | coon | dego | gook | guido | heeb | kike | kyke | jigaboo | negro | nigger | niglet | porchmonkey | pollock | ruski | sandnigger | wop') and language='den';
select language,text from delab_tweet where to_tsvector(text) @@ to_tsquery('Judensau | Kopftuchträger | Neger | Schlitzauge | Zigeuner | Schlampe | Schwuchtel | Nutte' ) and language='de'

