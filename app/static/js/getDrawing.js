

const baseURI = 'http://127.0.0.1:8000/';
var getDrawingURI = baseURI + 'create_embody';
//var getDrawingURI = baseURI + 'experiment/create_embody';

$(document).ready(function()  {

    var drawButtons = $(".embody-get-drawing");
    var imageContainer = $(".embody-image-container")
    var progressBarContainer = $(".progress")
    var progressBar = $("#image-loading-progress")

    // With sockets 
    function initConnection(socket) {
        socket.on('success', function(msg) {
            console.log(msg)
        });

        socket.on('progress', function(data) {
            progressBar.width(100*(data.done/data.from) + '%')
        });

        socket.on('end', function(img) {
            socket.disconnect()            

            // Draw image to statistic -page
            var source = img.path
            d = new Date()
            imageContainer.attr("src", "/static/" + source + "?" +d.getTime())

            // Remove progress bar
            progressBarContainer.addClass("hidden")
            progressBar.width('0%')
        });
    }


    drawButtons.click(function(event) {
        event.preventDefault()

        // Init socket
        var socket = io.connect(getDrawingURI);
        initConnection(socket)

        // 
        var pageId = this.dataset.value
        socket.emit('draw', {page:pageId})
        progressBarContainer.removeClass("hidden")

        /*
        With AJAX -calls
        var spinner = $(event.target.firstElementChild)
        spinner.removeClass("hidden")

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
        */

    })

})