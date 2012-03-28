/**
* Field Defenitions
*/
// html elements
var el_publish_dt_wrap = $('#date');
var el_slug_helper = $('#slug-helper');

// form fields
var f_title = $('#id_title');
var f_content = $('#id_content');
var f_slug = $('#id_slug');
var f_publish_dt = $('#id_publish_dt');
var f_status = $('#id_status');
var f_token = $('input[name="csrfmiddlewaretoken"]');

/**
* Date Picker Functionality
*/
var converter = new AnyTime.Converter();
var usable_converter = new AnyTime.Converter({
    format: '%a, %b %e %Y %h:%i %p'
});

// Anytime date picker
function toggle_anytime_picker(status) {
    if (status == 'draft') {
        f_publish_dt.AnyTime_noPicker();
    } else {
        var usable_converter = new AnyTime.Converter({
            format: '%a, %b %e %Y %h:%i %p'
        });

        try {
            var date = converter.parse(f_publish_dt[0].value);
            f_publish_dt[0].value = usable_converter.format(date);
        } catch(e) {
            // pass
        }

        f_publish_dt.AnyTime_picker({
            format: '%a, %b %e %Y %h:%i %p'
        });
    }
}

function toggle_publish_dt(status) {
    if (status == 'published') {
        el_publish_dt_wrap.show();
        f_publish_dt.removeAttr('disabled');
        toggle_anytime_picker(status);
    }
    if (status == 'draft') {
        el_publish_dt_wrap.hide();
        toggle_anytime_picker(status);
    } 
}

f_status.change(function() {
    toggle_publish_dt(this.value);
})

// toggle on load if published
if (f_status[0].value == 'published') {
    toggle_publish_dt(f_status[0].value);
}

/**
* Content Inserts
*/
$(".media-item a").click(function(){
    $("#id_content").insertAtCaret($(this).attr('data-shortcode'));
    return false;
});

/**
* Auto-slug generation
*/
function write_slug(value) {
    value = value.replace(/[^\w]+/ig,'-');
    value = value.toLowerCase();
    value = value.substring(0, 65);

    if (f_slug.val().length  <= 0) {
        f_slug.val(value);
        el_slug_helper.html(value);
    }
}

f_title.blur(function() {
    var value = $(this).val();
    write_slug(value);
});

/**
* Tooltips
*/
$('a[rel=tooltip]').tooltip();

/**
* Preview Mode
**/
function show_preview(xhr, status) {
    if (status == 'success') {
        var el_preview = $('#preview-modal');
        var html = xhr.responseText;
        el_preview.find('.modal-body').html(html);
        el_preview.modal();
    }
}

function query_preview() {
    var url = '/admin/preview/';
    var data = {
        title: f_title.val(),
        content: f_content.val(),
        csrfmiddlewaretoken: f_token.val()
    }

    $.ajax(url, {
        type: 'POST',
        data: data,
        complete: function(xhr, status) {
            show_preview(xhr, status);
        }
    });
}

$(document).bind('keydown', 'ctrl+shift+q', query_preview);
f_title.bind('keydown', 'ctrl+shift+q', query_preview);
f_content.bind('keydown', 'ctrl+shift+q', query_preview);
f_slug.bind('keydown', 'ctrl+shift+q', query_preview);
