import QtQuick 2.9

Item {
    id: root
    width: 400
    height: 400

    property real value: 0
    property real minValue: 0
    property real maxValue: 8000
    property string unit: "RPM"

    property color primaryColor: "#16CCBA"
    property color secondaryColor: "#00000000"
    property int animationDuration: 1000
    property real startAngle: 0

    Rectangle {
        anchors.fill: parent
        color: "#041F2B"
        z: -1
    }

    Image {
        id: background1
        source: "./assets/Ellipse 5.svg"
        rotation: 180
        sourceSize.width: width
        sourceSize.height: width
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
        anchors.centerIn: parent
        scale: 1
        opacity: 0.7
        z: 0
    }

    Image {
        id: background2
        source: "./assets/Ellipse 1.svg"
        sourceSize.width: width
        sourceSize.height: width
        anchors.fill: parent
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        scale: 1
        opacity: 0.7
        z: 1
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        antialiasing: true
        property real degree: 0

        onDegreeChanged: requestPaint()

        onPaint: {
            var ctx = getContext("2d")
            var center = Qt.point(width / 2, height / 2)
            var side = Math.min(width, height)
            var radius = (side - side * 0.20) / 2
            var startAngle = Math.PI * 3 / 4
            var fullAngle = Math.PI * 3 / 2
            var progressAngle = startAngle + (degree / 270) * fullAngle

            ctx.reset()
            ctx.lineCap = 'round'

            ctx.lineWidth = side * 0.1
            ctx.beginPath()
            ctx.arc(center.x, center.y, radius, startAngle, progressAngle)
            ctx.strokeStyle = secondaryColor
            ctx.stroke()

            ctx.lineWidth = 20
            ctx.beginPath()
            ctx.arc(center.x, center.y, radius, startAngle, progressAngle)
            ctx.strokeStyle = primaryColor
            ctx.stroke()

            // draw tick marks
            ctx.lineWidth = 10
            ctx.strokeStyle = '#FFFFFF'
            ctx.beginPath()
            var tickCount = 2; // Number of tick marks
            for (var i = 0; i < tickCount; i++) {
                var angle = startAngle + (i / (tickCount - 1)) * (progressAngle - startAngle)
                var x1 = center.x + radius * Math.cos(angle)
                var y1 = center.y + radius * Math.sin(angle)
                var x2 = center.x + (radius - 20) * Math.cos(angle)
                var y2 = center.y + (radius - 20) * Math.sin(angle)
                ctx.moveTo(x1, y1)
                ctx.lineTo(x2, y2)
            }
            ctx.stroke()
        }
    }

    Text {
        id: gaugeText
        anchors.centerIn: parent
        text: "0"
        font.pixelSize: 0.2 * Math.min(root.width, root.height)
        font.bold: true
        color: "#FFFFFF"
    }

    Text {
        id: gaugeUnit
        anchors.top: gaugeText.bottom
        anchors.horizontalCenter: gaugeText.horizontalCenter
        
        text: unit
        font.pixelSize: 18
        font.bold: true
        color: "#FFFFFF" 
    }

    Behavior on value {
        NumberAnimation { duration: animationDuration }
    }
    
    onValueChanged: updateGaugeValue(value)

    function updateGaugeValue(value) {
        canvas.degree = value * 270
        gaugeText.text = (value * (maxValue - minValue) + minValue).toFixed(0)
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true

        property bool isDragging: false
        property real initialValue: 0

        onEntered: cursorShape = Qt.PointingHandCursor
        onPressed: {
            isDragging = true
            initialValue = root.value
        }
        onReleased: isDragging = false

        onMouseXChanged: updateDragValue(mouse.x, mouse.y)
        onMouseYChanged: updateDragValue(mouse.x, mouse.y)

        function updateDragValue(x, y) {
            if (!isDragging) return

            var centerX = width / 2
            var centerY = height / 2
            var dx = x - centerX
            var dy = centerY - y // Note: y-axis is inverted
            var angle = Math.atan2(dy, dx) * (180 / Math.PI)

            // Convert angle to gauge value (0 to 1)
            var gaugeValue = (angle + 135) / 270 // Adjust based on your gauge's start angle
            gaugeValue = Math.max(0, Math.min(gaugeValue, 1)) // Clamp value

            root.value = gaugeValue
        }
    }
}
