

const url = 'http://127.0.0.1:8000/';

$(document).ready(function() {

    try {
        var canvas = $("#embody-canvas")
        var context = document.getElementById("embody-canvas").getContext("2d");

        // Base image
        var img = document.getElementById("baseImage");

        console.log(img)
        console.log(canvas)
    } catch (e) {
        console.log(e)
        if (e instanceof TypeError) {
            return
        }
    }

    // Init draw variables
    var clickX = new Array();
    var clickY = new Array();
    var clickDrag = new Array();
    var paint;
    var drawRadius=15;

    // Click handlers
    canvas.mousedown(function(e){
        var mouseX = e.pageX - this.offsetLeft;
        var mouseY = e.pageY - this.offsetTop;
        paint = true;

        if (pointInsideBaseImage([mouseX, mouseY])) {
            addClick(mouseX, mouseY);
            redraw();
        }
    });

    canvas.mousemove(function(e){
        // TODO: if mousedown -> can draw outside of image
        var mouseX = e.pageX - this.offsetLeft;
        var mouseY = e.pageY - this.offsetTop;
        if(paint && pointInsideBaseImage([mouseX, mouseY])){
          addClick(mouseX, mouseY, true);
          redraw();
        }
    });

    canvas.mouseup(function(e){
        paint = false;
    });

    canvas.mouseleave(function(e){
        paint = false;
    });

    // TODO: changing drawradius doesnt affect to the saved datapoints !!!
    // Bigger brush should make more datapoints compared to smaller ones.
    $(".canvas-container").bind('DOMMouseScroll',function(event) {
        //event.preventDefault()

        // Change brush size
        if (event.originalEvent.detail >= 0){
            if (drawRadius >= 15) {
                drawRadius -= 5; 
            }
        } else {
            if (drawRadius <= 15) {
                drawRadius += 5; 
            }
        }

        // Show brush size to user
        if (drawRadius == 10) {
            this.firstElementChild.innerHTML = "small brush"
        } else if (drawRadius == 15) {
            this.firstElementChild.innerHTML = "normal brush"
        } else if (drawRadius == 20) {
            this.firstElementChild.innerHTML = "large brush"
        }
    })

    $(".clear-button").on('click', function() {
        clearCanvas()
    })

    $(".next-page").click(function() {
        saveData()
    })


    // Draw methods
    function addClick(x, y, dragging=false)
    {
        clickX.push(x);
        clickY.push(y);
        clickDrag.push(dragging);
    }

    function drawPoint(x, y, radius) {
        context.beginPath();
        context.arc(x, y, radius, 0, 2 * Math.PI, false);
        context.fill()
    }

    function isWhite(color) {
        if (color === 255) 
            return true
        return false
    }

    // Method for checking if cursor is inside human body before creating brush stroke
    function pointInsideBaseImage(point) {
        var imageData = context.getImageData(point[0], point[1],1,1)

        startR = imageData.data[0];
        startG = imageData.data[1];
        startB = imageData.data[2];

        if (isWhite(startB) && isWhite(startG) && isWhite(startR)) {
            return false;
        }

        return true;
    }

    function redraw(){

        /* 
        Check:
        https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/globalCompositeOperation

        TODO: It's possible to use only one mask image propably
        */
        //context.globalCompositeOperation='destination-over' // 
        //context.clearRect(0, 0, context.canvas.width, context.canvas.height); // Clears the canvas

        lastX = clickX[clickX.length - 1]
        lastY = clickY[clickY.length - 1]

        // Opacity (there was 0.2 opacity in the old version):
        context.globalAlpha = 0.2
        
        // Gradient:
        var gradient = context.createRadialGradient(lastX, lastY, 1, lastX, lastY, drawRadius);
        gradient.addColorStop(0, "rgba(255,0,0,1)");
        gradient.addColorStop(1, "rgba(255,0,0,0.1)");
        context.fillStyle = gradient

        // Draw circle with gradient
        drawPoint(lastX, lastY, drawRadius)

        /*
        OLD version, where line is drawn continuously (not needed probably)

        for(var i=0; i < clickX.length; i++) {		

            context.beginPath();

            if (clickDrag[i] && i) { 
                context.moveTo(clickX[i-1], clickY[i-1]);
            } else {
                context.moveTo(clickX[i]-1, clickY[i]);
            }

            context.lineTo(clickX[i], clickY[i]);
            context.closePath();
            context.stroke();
        }
        */
    }

    // This is not needed, because canvas dont allow to draw on white points (mask points)
    function drawMaskToBaseImage()
    {
        var img = document.getElementById("baseImageMask");
        context.globalAlpha = 1
        context.drawImage(img, 0, 0);
    }

    function drawBaseImage()
    {
        var width = img.width;
        var height = img.height;

        context.canvas.height = height
        context.canvas.width = width
        context.drawImage(img, 0, 0);
        img.classList.add("hidden")
    }

    function clearCanvas() {
        // Clear canvas
        img.classList.remove("hidden")
        context.clearRect(0, 0, context.canvas.width, context.canvas.height);
        drawBaseImage()

        // Remove saved coordinates
        clickX = []
        clickY = []
        clickDrag = []
    }

    function saveData() {

        var points = {
            x: clickX,
            y: clickY
        }

        points = JSON.stringify(points)

        console.log(points)

        $("#canvas-data").val(points);
        $("#canvas-form").submit();

    }

    drawBaseImage()

});