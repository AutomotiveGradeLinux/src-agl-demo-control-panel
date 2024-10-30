import QtQuick 2.9
import QtQuick.Controls 2.2
import QtQuick.Layouts 1.3

Item {
    id: root
    width: 400
    height: 400

    property string carImage: "./assets/car-top.png"
    property string defaultTire: "./assets/DefaultTire.svg"
    property string selectedTire: "./assets/SelectedTire.svg"

    property color highlight: "#4BD7D6"
    property color defaultColor: "#6C6C85"
    property color darkbg: "#131313"

    property int selectedTireIndex: -1
    signal valueChanged(int newValue)

    // Move these functions here so they're accessible to all buttons
    function resetAllButtons() {
        selectedTireIndex = -1;
        button0.background.color = defaultColor;
        button1.background.color = defaultColor;
        button2.background.color = defaultColor;
        button3.background.color = defaultColor;
        
        tireImage0.source = defaultTire;
        tireImage1.source = defaultTire;
        tireImage2.source = defaultTire;
        tireImage3.source = defaultTire;
    }

    function selectButton(index) {
        selectedTireIndex = index;
        valueChanged(index);
        
        switch(index) {
            case 0:
                button0.background.color = highlight;
                tireImage0.source = selectedTire;
                break;
            case 1:
                button1.background.color = highlight;
                tireImage1.source = selectedTire;
                break;
            case 2:
                button2.background.color = highlight;
                tireImage2.source = selectedTire;
                break;
            case 3:
                button3.background.color = highlight;
                tireImage3.source = selectedTire;
                break;
        }
        
        // Reset other buttons
        for (var i = 0; i < 4; i++) {
            if (i !== index) {
                var button = eval("button" + i);
                button.background.color = defaultColor;
                eval("tireImage" + i).source = defaultTire;
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: darkbg
        z: 0

        Image {
            id: car
            source: carImage
            fillMode: Image.PreserveAspectFit
            anchors.fill: parent
            anchors.centerIn: parent
            z: 1
        }

        GridLayout {
            id: buttonGrid
            anchors.centerIn: parent
            columns: 2
            rows: 2
            
            Button {
                id: button0
                Layout.preferredWidth: car.width / 2
                Layout.preferredHeight: car.height / 2
                
                background: Rectangle {
                    color: defaultColor
                    opacity: 0.5
                    radius: 15
                    z: 1
                }

                Rectangle {
                    width: parent.width / 2
                    height: parent.height / 2
                    color: "transparent"
                    anchors.fill: parent
                    z: 2
                    
                    Image {
                        id: tireImage0
                        source: defaultTire
                        sourceSize.height: parent.height / 2
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: parent.height * 0.32
                    }
                }

                onClicked: handleButtonClick(0)

                function handleButtonClick(index) {
                    if (selectedTireIndex === index) {
                        resetAllButtons();
                    } else {
                        selectButton(index);
                    }
                }
            }

            Button {
                id: button1
                Layout.preferredWidth: car.width / 2
                Layout.preferredHeight: car.height / 2
                
                background: Rectangle {
                    color: defaultColor
                    opacity: 0.5
                    radius: 15
                    z: 1
                }

                Rectangle {
                    width: parent.width / 2
                    height: parent.height / 2
                    color: "transparent"
                    anchors.fill: parent
                    z: 2
                    
                    Image {
                        id: tireImage1
                        source: defaultTire
                        sourceSize.height: parent.height / 2
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: parent.height * 0.28
                    }
                }

                onClicked: handleButtonClick(1)

                function handleButtonClick(index) {
                    if (selectedTireIndex === index) {
                        resetAllButtons();
                    } else {
                        selectButton(index);
                    }
                }
            }

            Button {
                id: button2
                Layout.preferredWidth: car.width / 2
                Layout.preferredHeight: car.height / 2
                
                background: Rectangle {
                    color: defaultColor
                    opacity: 0.5
                    radius: 15
                    z: 1
                }

                Rectangle {
                    width: parent.width / 2
                    height: parent.height / 2
                    color: "transparent"
                    anchors.fill: parent
                    z: 2
                    
                    Image {
                        id: tireImage2
                        source: defaultTire
                        sourceSize.height: parent.height / 2
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: parent.height * 0.32
                    }
                }

                onClicked: handleButtonClick(2)

                function handleButtonClick(index) {
                    if (selectedTireIndex === index) {
                        resetAllButtons();
                    } else {
                        selectButton(index);
                    }
                }
            }

            Button {
                id: button3
                Layout.preferredWidth: car.width / 2
                Layout.preferredHeight: car.height / 2
                
                background: Rectangle {
                    color: defaultColor
                    opacity: 0.5
                    radius: 15
                    z: 1
                }

                Rectangle {
                    width: parent.width / 2
                    height: parent.height / 2
                    color: "transparent"
                    anchors.fill: parent
                    z: 2
                    
                    Image {
                        id: tireImage3
                        source: defaultTire
                        sourceSize.height: parent.height / 2
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: parent.height * 0.28
                    }
                }

                onClicked: handleButtonClick(3)

                function handleButtonClick(index) {
                    if (selectedTireIndex === index) {
                        resetAllButtons();
                    } else {
                        selectButton(index);
                    }
                }
            }
        }
    }
}
