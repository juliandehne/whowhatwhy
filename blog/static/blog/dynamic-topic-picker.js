$(document).ready(function () {
    $(function () {
        $("a.dynamic-topic").click(function (e) {
            e.preventDefault();
            original_url = e.target.href;
            topic_entered = $('#topic-input').val();
            log_url = original_url.replace("topic", topic_entered);
            console.log(log_url)
            window.open(log_url)
        });
    });
});
