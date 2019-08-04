$(document).ready( function () {
    $('#loans').DataTable({
        paging: false,
        searching: false,
        info: false
    });

    $('#cashflow').DataTable({
        paging: false,
        searching: false,
        info: false
    });

    $('#total-cost').DataTable({
        paging: false,
        searching: false,
        info: false
    })


    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    Array.prototype.slice.apply(document.getElementsByClassName("delete-item")).forEach((delete_button) =>
        delete_button.onclick = function(event){
            let loan_to_delete = this.dataset.id;
            let jsonData = { loan: loan_to_delete };

            $.ajax({
                "type": "DELETE",
                "dataType": "json",
                "url": "/delete_loan/",
                "data": jsonData,
                "success": function(result) {
                    window.location.href = '/';
                },
                error : function(xhr,errmsg,err) {
                    console.log("something went wrong...")
                }
            });
        }
    )

} );