$(document).ready(function () {
    $('body').keypress(function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            $("#submitButton").click();
        }
    });
});

