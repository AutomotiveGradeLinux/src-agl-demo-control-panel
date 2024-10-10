import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Controls 2.2

Rectangle {
    width: frame.implicitWidth
    height: frame.implicitHeight
    
    // save colors in variables
    property color backgroundColor: "#131313"
    property color background_alt: "#2A2827"
    property color buttonColor: "#6C6C85"
    property color highlight: "#4BD7D6"

    // store icons from qrc in variables
    property string iconUp: "qrc:/Carbon_Icons/carbon_icons/temperature--frigid.svg"
    property string iconDown: "qrc:/Carbon_Icons/carbon_icons/temperature--hot.svg"

    color: backgroundColor
    
    signal valueChanged(int newValue)

    FontMetrics {
        id: fontMetrics
    }

    Component {
        id: delegateComponent

        Label {
            text: model.number
            opacity: 1.0 - Math.abs(Tumbler.displacement) / (Tumbler.tumbler.visibleItemCount / 2)
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: fontMetrics.font.pixelSize * parent.width / fontMetrics.font.pixelSize / 3
            color: highlight
            font.bold: true
        }
    }

    Frame {
        id: frame
        padding: 0
        anchors.centerIn: parent
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            color: backgroundColor
            radius: 10
        }

        Column {
            spacing: 10
            anchors.fill: parent

            anchors.horizontalCenter: parent.horizontalCenter
            anchors.margins: 10

            Button {
                width: parent.width
                height: parent.height / 6

                Rectangle {
                    width: parent.width
                    height: parent.height
                    color: buttonColor
                    radius: 10
                    
                    Image {
                        source: iconUp
                        anchors.centerIn: parent
                        sourceSize.width: parent.width / 2
                        sourceSize.height: parent.height / 2
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                    }
                }
                onClicked: {
                    // if we are at the top of the list, set the index to the last element
                    if (valueTumbler.currentIndex == 0) {
                        valueTumbler.currentIndex = valueTumbler.model.count - 1;
                    }
                    else {
                        valueTumbler.currentIndex -= 1;
                    }
                }
            }

            Tumbler {
                id: valueTumbler
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width
                height: parent.height / 2
                model: ListModel {
                    ListElement { number: 16 }
                    ListElement { number: 17 }
                    ListElement { number: 18 }
                    ListElement { number: 19 }
                    ListElement { number: 20 }
                    ListElement { number: 21 }
                    ListElement { number: 22 }
                    ListElement { number: 23 }
                    ListElement { number: 24 }
                    ListElement { number: 25 }
                    ListElement { number: 26 }
                    ListElement { number: 27 }
                    ListElement { number: 28 }
                    ListElement { number: 29 }
                    ListElement { number: 30 }
                    ListElement { number: 31 }
                    ListElement { number: 32 }
                }

                onCurrentIndexChanged: {
                    valueChanged(model.get(currentIndex).number);
                }

                delegate: delegateComponent

                Rectangle {
                    width: parent.width
                    height: parent.height
                    color: background_alt
                    radius: 10
                }
            }

            Button {
                width: parent.width
                height: parent.height / 6

                Rectangle {
                    width: parent.width
                    height: parent.height
                    color: buttonColor
                    radius: 10
                    
                    Image {
                        source: iconDown
                        anchors.centerIn: parent
                        sourceSize.width: parent.width / 2
                        sourceSize.height: parent.height / 2
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                    }
                }
                onClicked: {
                    if (valueTumbler.currentIndex == 16) {
                        valueTumbler.currentIndex = 0;
                    }
                    else {
                        valueTumbler.currentIndex += 1;
                    }
                }
            }
        }      
    }
}