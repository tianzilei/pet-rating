

const baseURI = 'http://127.0.0.1:8000/';
var getDrawingURI = baseURI + 'experiment/create_embody';


$(document).ready(function()  {

    var drawButtons = $(".embody-get-drawing");
    var imageContainer = $(".embody-image-container")
    var source = ''

    drawButtons.click(function(event) {
        event.preventDefault()

        var spinner = $(event.target.firstElementChild)
        spinner.removeClass("hidden")

        var pageId = this.dataset.value

        $.ajax({
            url: getDrawingURI,
            method: 'POST',
            data: {page:pageId}
        }).done(function(data) {
            var source = JSON.parse(data).path;
            console.log(source)
            d = new Date()
            imageContainer.attr("src", "/static/" + source + "?" +d.getTime())
            spinner.addClass("hidden")
        })

    })

})