$(document).ready(function() {
    const error_handler = function(f) {
        const msg = f.responseJSON.error || "Failed (" + f.status + ")";
        $("#error-msg").text(msg);
    }

    $(".update-timed-release").submit(function (e) {
        e.preventDefault();
        $("#error-msg").text("");
        const params = {};
        $(this).serializeArray().forEach(function (x) {
            params[x.name] = x.value;
        });

        $.post(script_root + $(this).attr("action"), params, function (data) {
            location.reload(true);
        }).fail(error_handler);
    });
});
