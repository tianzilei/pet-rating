

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

    function addClick(x, y, dragging)
    {
        clickX.push(x);
        clickY.push(y);

        // ClickDrag array is unnecessary beacause all the coordinates are saved to
        // X & Y -arrays
        clickDrag.push(dragging);
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
        var gradient = context.createRadialGradient(lastX, lastY, 1, lastX, lastY, 15);
        gradient.addColorStop(0, "rgba(255,0,0,1)");
        gradient.addColorStop(1, "rgba(255,0,0,0.1)");

        // Draw circle with gradient
        context.beginPath();
        context.arc(lastX, lastY, 15, 0, 2 * Math.PI, false);
        context.fillStyle = gradient
        context.fill()

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