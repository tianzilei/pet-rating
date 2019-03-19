

$(document).ready(function() {


    $("#canvas-data").val("hello world");
    var canvas = $("#embody-canvas")
    var context = document.getElementById("embody-canvas").getContext("2d");

    canvas.mousedown(function(e){
        var mouseX = e.pageX - this.offsetLeft;
        var mouseY = e.pageY - this.offsetTop;
              
        paint = true;
        addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop);
        redraw();
    });

    canvas.mousemove(function(e){
        if(paint){
          addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true);
          redraw();
        }
    });

    canvas.mouseup(function(e){
        paint = false;
    });

    canvas.mouseleave(function(e){
        paint = false;
    });

    var clickX = new Array();
    var clickY = new Array();
    var clickDrag = new Array();
    var paint;
    var drawRadius=15;

    // TODO: changing drawradius doesnt affect to the saved datapoints !!!
    // Bigger brush should make more datapoints compared to smaller ones.
    $(".canvas-container").bind('DOMMouseScroll',function(event) {
        event.preventDefault()

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

    function addClick(x, y, dragging)
    {
        clickX.push(x);
        clickY.push(y);

        // ClickDrag array is unnecessary beacause all the coordinates are saved to
        // X & Y -arrays
        clickDrag.push(dragging);
    }

    function drawPoint(x, y, radius) {
        context.beginPath();
        context.arc(x, y, radius, 0, 2 * Math.PI, false);
        context.fill()
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
        drawPoint(lastX + 3, lastY, drawRadius)
        drawPoint(lastX - 3, lastY, drawRadius)
        drawPoint(lastX, lastY + 3, drawRadius)
        drawPoint(lastX, lastY - 3, drawRadius)
        */
        drawMaskToBaseImage()

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

    function drawMaskToBaseImage()
    {
        var img = document.getElementById("baseImageMask");
        context.globalAlpha = 1
        context.drawImage(img, 0, 0);
    }

    function drawBaseImage()
    {
        var img = document.getElementById("baseImage");
        var width = img.clientWidth;
        var height = img.clientHeight;

        context.canvas.height = height
        context.canvas.width = width
        context.drawImage(img, 0, 0);
        img.classList.add("hidden")
    }

    drawBaseImage()

});