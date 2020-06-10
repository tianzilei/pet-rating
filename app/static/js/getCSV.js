


$(document).ready(function()  {

    var exportButton = $(".get-csv-results");

    var progressBarContainer = $(".progress")
    var progressBar = $("#export-results-bar")

    var exportLinkContainer = $("#export-link-container");
    var exportLink = $("#export-link");
    var exportError = $("#export-error");

    // With sockets 
    function initConnection(socket) {

        socket.on('success', function(msg) {
            exportButton.text('Generating file...')
            exportButton.addClass('disabled')
        });

        socket.on('progress', function(data) {
            console.log(data)
            progressBar.width(100*(data.done/data.from) + '%')
        });

        socket.on('timeout', function(data) {
            console.log("timeout error", data.exc)
            socket.disconnect()            
            exportButton.text('Export results')
            exportButton.removeClass('disabled')
            progressBarContainer.addClass("hidden")

            exportLinkContainer.removeClass("hidden")
            exportError.text('Error: ' + data.exc)
        });

        socket.on('file_ready', function(file) {
            socket.disconnect()            

            exportButton.text('File is ready!')

            exportLinkContainer.removeClass("hidden")

            var href = exportLink.attr('href');

            href += '&path=' + file.path
            $(exportLink).attr('href', href);

            // Remove progress bar
            progressBarContainer.addClass("hidden")
            progressBar.width('0%')

            exportLink.text('Download: ' + file.filename + '.csv')
        });
    }


    exportButton.click(function(event) {
        event.preventDefault()

        // Init socket
        var socket = io.connect(exportURL);
        initConnection(socket)

        socket.emit('generate_csv', {exp_id: this.dataset.value})

        progressBarContainer.removeClass("hidden")

    })


})
