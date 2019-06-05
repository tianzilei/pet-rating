


$( document ).ready( function() {
    $('#embody-file-input').change(function(filename) {

        var fileName = $(this).val();
        //replace the "Choose a file" label
        $(this).next('.custom-file-label').html(fileName);

        $('.submit-file').prop("disabled", false);
    })
})
