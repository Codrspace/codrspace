var el_publish_dt_wrap = $('#date');
var el_publish_dt = $('#id_publish_dt');
var el_status = $('#id_status');
var converter = new AnyTime.Converter();
var usable_converter = new AnyTime.Converter({
    format: '%a, %b %e %Y %h:%i %p'
});

/* Anytime date picker */
function toggle_anytime_picker(status) {
    if (status == 'draft') {
        el_publish_dt.AnyTime_noPicker();
    } else {
        var usable_converter = new AnyTime.Converter({
            format: '%a, %b %e %Y %h:%i %p'
        });

        try {
            var date = converter.parse(el_publish_dt[0].value);
            el_publish_dt[0].value = usable_converter.format(date);
        } catch(e) {
            // pass
        }

        el_publish_dt.AnyTime_picker({
            format: '%a, %b %e %Y %h:%i %p'
        });
    }
}

function toggle_publish_dt(status) {
    if (status == 'published') {
        el_publish_dt_wrap.show();
        el_publish_dt.removeAttr('disabled');
        toggle_anytime_picker(status);
    }
    if (status == 'draft') {
        el_publish_dt_wrap.hide();
        toggle_anytime_picker(status);
    } 
}

/* Publish status toggle for publish_dt */
el_status.change(function() {
    toggle_publish_dt(this.value);
})

// toggle on load if published
if (el_status[0].value == 'published') {
    toggle_publish_dt(el_status[0].value);
}

/* Helper to insert media at cursor location in content field */
$(".media-item a").click(function(){
    $("#id_content").insertAtCaret($(this).attr('data-shortcode'));
    return false;
});

/* slug autogenerate */
var title_field = $('#id_title');
var slug_field = $('#id_slug');
var slug_helper = $('#slug-helper');

function write_slug(value) {
    value = value.replace(/[^\w]+/ig,'-');
    value = value.toLowerCase();
    value = value.substring(0, 65);

    if (slug_field.val().length  <= 0) {
        slug_field.val(value);
        slug_helper.html(value);
    }
}

title_field.blur(function() {
    var value = $(this).val();
    write_slug(value);
});

/* tooltips */
$('a[rel=tooltip]').tooltip();
