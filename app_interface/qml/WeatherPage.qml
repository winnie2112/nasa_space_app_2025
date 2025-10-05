import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Dialogs

RowLayout {
    signal backClicked()

    anchors.fill: parent

    property string liveTime: ""

    Timer {
        interval: 120000
        running: true
        repeat: true
        onTriggered: weather_components.update_current_status()
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: weather_components.tick_local_time()
    }

    Connections {
        target: weather_components
        function onLive_local_time_changed() {
            liveTime = weather_components.live_local_time
        }
        function onError_message(error) {
            errorDialog.text = error;
            errorDialog.open();
        }
    }

    MessageDialog {
        id: errorDialog
        buttons: MessageDialog.Ok
        text: "Connection timeout."
    }

    ColumnLayout {
        Layout.preferredWidth: parent.width * 0.5
        Layout.preferredHeight: parent.height
        Layout.leftMargin: 10
        Layout.topMargin: 15

        spacing: 10

        Column {

            spacing: 5

            TextInput {
                id: currentLocation
                text: qsTr("LIVE Detected IP Location")
                color: "#e8def0"
                font.bold: true
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 13
                antialiasing: false
                renderType: Text.NativeRendering
            }

            Rectangle {
                id: displayLocationInfos
                width: 200
                height: 100
                color: "#90BABAEE"

                Text {
                    id: textDisplayParams
                    anchors.centerIn: parent
                    color: "white"
                    font.bold: true
                    font.family: "../resources/m5x7.ttf"
                    font.pixelSize: 13
                    antialiasing: false
                    renderType: Text.NativeRendering
                    text: (
                        weather_components.ip_message +
                        " " + liveTime + "\n" +
                        weather_components.timezone_name
                    )
                }
            }
        }

        Column {
            spacing: 5
            Label {
                text: "Enter Location-Empty to reset"
                color: "#e8def0"
                font.bold: true
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 14
                antialiasing: false
                renderType: Text.NativeRendering
            }

            TextField {
                id: locationInput
                placeholderText: "City, Country"
                color: "white"
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 15
                antialiasing: false
                renderType: Text.NativeRendering

                implicitWidth: 200

                background: Rectangle {
                    width: parent.width
                    color: "#90BABAEE"
                }

                onTextChanged: weather_components.input_location = text
                Component.onCompleted: text = weather_components.input_location
            }
        }

        Column {
            spacing: 5
            visible: !detect6Monthscheck.checked
            Label {
                text: "Forecast in next 7 days"
                color: "#e8def0"
                font.bold: true
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 14
                antialiasing: false
                renderType: Text.NativeRendering
            }

            ComboBox {
                id: dateModels
                model: weather_components.choose_forecast_dates()
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 15
                implicitWidth: 200

                onCurrentTextChanged: {
                    weather_components.selected_date = currentText
                }

                // main rectangle for the ComboBox
                background: Rectangle {
                    implicitWidth: 120
                    implicitHeight: 40
                    border.color: "#90BABAEE"
                    border.width: dateModels.visualFocus ? 2 : 1
                    radius: 2
                    color: "#90BABAEE"
                }

                //text of main rectangle
                contentItem: Text {
                    leftPadding: 0
                    rightPadding: dateModels.indicator.width + dateModels.spacing

                    text: dateModels.displayText
                    font: dateModels.font
                    color: "white"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                //text of each option in the drop-down menu
                delegate: ItemDelegate {
                    id: delegateDateModels

                    required property var model
                    required property int index

                    width: dateModels.width

                    background: Rectangle {
                        color: delegateDateModels.highlighted ? "#e8def0" : "#90BABAEE"
                        opacity: 0.9
                    }

                    contentItem: Text {
                        text: delegateDateModels.model[dateModels.textRole]
                        color: "white"
                        font: dateModels.font
                        elide: Text.ElideRight
                        verticalAlignment: Text.AlignVCenter
                    }
                    highlighted: dateModels.highlightedIndex === index
                }

                // arrow icon
                indicator: Canvas {
                    id: canvasdateModel
                    x: dateModels.width - width - dateModels.rightPadding
                    y: dateModels.topPadding + (dateModels.availableHeight - height) / 2
                    width: 12
                    height: 8
                    contextType: "2d"

                    Connections {
                        target: dateModels
                        function onPressedChanged() { canvasdateModel.requestPaint(); }
                    }

                    onPaint: {
                        context.reset();
                        context.moveTo(0, 0);
                        context.lineTo(width, 0);
                        context.lineTo(width / 2, height);
                        context.closePath();
                        context.fillStyle = "white";
                        context.fill();
                    }
                }

                // container for the drop-down list
                popup: Popup {
                    y: dateModels.height - 1
                    width: dateModels.width
                    height: Math.min(contentItem.implicitHeight, dateModels.Window.height - topMargin - bottomMargin)
                    padding: 1

                    contentItem: ListView {
                        clip: true
                        implicitHeight: contentHeight
                        model: dateModels.popup.visible ? dateModels.delegateModel : null
                        currentIndex: dateModels.highlightedIndex

                        ScrollIndicator.vertical: ScrollIndicator { }
                    }

                    background: Rectangle {
                        border.color: "#90BABAEE"
                        color: "#90BABAEE"
                        radius: 2
                    }
                }
            }
        }

        Column {
            spacing: 5

            CheckBox {
                id: detect6Monthscheck
                text: "Forecast after 7 days?"
                Component.onCompleted: checked = weather_components.est_input_date_check
                onCheckedChanged: weather_components.est_input_date_check = checked
            }

            Label {
                text: "Weather in next 6 Months"
                color: "#e8def0"
                font.bold: true
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 14
                antialiasing: false
                renderType: Text.NativeRendering
                visible: detect6Monthscheck.checked
            }

            TextField {
                id: estDate6Months
                placeholderText: "YYYY-MM-DD"
                color: "white"
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 15
                antialiasing: false
                renderType: Text.NativeRendering
                visible: detect6Monthscheck.checked

                implicitWidth: 200

                background: Rectangle {
                    width: parent.width
                    color: "#90BABAEE"
                }

                validator: RegularExpressionValidator { regularExpression: /^\d{4}-\d{2}-\d{2}$/ }
                onTextChanged: weather_components.est_input_date = text
                Component.onCompleted: text = weather_components.est_input_date
            }

            //SwipeView {
            //    id: monthView
            //    width: 200; height: 150
            //    clip: true
            //    Repeater {
            //        model: CalendarModel {
            //            from: minDate
            //            to: maxDate
            //        }
            //        MonthGrid {
            //            width: monthView.width
            //            height: monthView.height
            //            month: model.month
            //            year: model.year
            //            locale: Qt.locale("en_US")
            //        }
            //    }
            //}
            //Row {
            //    Button {
            //        text: "←"
            //        onClicked: monthView.decrementCurrentIndex()
            //    }
            //    Button {
            //        text: "→"
            //        onClicked: monthView.incrementCurrentIndex()
            //    }
            //}
        }

        Column {
            spacing: 5
            visible: !detect6Monthscheck.checked
            Label {
                text: "Climate Models"
                color: "#e8def0"
                font.bold: true
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 15
                antialiasing: false
                renderType: Text.NativeRendering
            }

            ComboBox {
                id: climateModels
                model: weather_components.model_map
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 15
                implicitWidth: 200

                onCurrentTextChanged: {
                    weather_components.weather_models = currentText
                }
                Component.onCompleted: {
                    currentIndex = weather_components.model_map.indexOf(
                        weather_components.weather_models
                    )
                }

                // main rectangle for the ComboBox
                background: Rectangle {
                    implicitWidth: 120
                    implicitHeight: 40
                    border.color: "#90BABAEE"
                    border.width: climateModels.visualFocus ? 2 : 1
                    radius: 2
                    color: "#90BABAEE"
                }

                //text of main rectangle
                contentItem: Text {
                    leftPadding: 0
                    rightPadding: climateModels.indicator.width + climateModels.spacing

                    text: climateModels.displayText
                    font: climateModels.font
                    color: "white"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                //text of each option in the drop-down menu
                delegate: ItemDelegate {
                    id: delegate

                    required property var model
                    required property int index

                    width: climateModels.width

                    background: Rectangle {
                        color: delegate.highlighted ? "#e8def0" : "#90BABAEE"
                        opacity: 0.9
                    }

                    contentItem: Text {
                        text: delegate.model[climateModels.textRole]
                        color: "white"
                        font: climateModels.font
                        elide: Text.ElideRight
                        verticalAlignment: Text.AlignVCenter
                    }
                    highlighted: climateModels.highlightedIndex === index
                }

                // arrow icon
                indicator: Canvas {
                    id: canvas
                    x: climateModels.width - width - climateModels.rightPadding
                    y: climateModels.topPadding + (climateModels.availableHeight - height) / 2
                    width: 12
                    height: 8
                    contextType: "2d"

                    Connections {
                        target: climateModels
                        function onPressedChanged() { canvas.requestPaint(); }
                    }

                    onPaint: {
                        context.reset();
                        context.moveTo(0, 0);
                        context.lineTo(width, 0);
                        context.lineTo(width / 2, height);
                        context.closePath();
                        context.fillStyle = "white";
                        context.fill();
                    }
                }

                // container for the drop-down list
                popup: Popup {
                    y: climateModels.height - 1
                    width: climateModels.width
                    height: Math.min(contentItem.implicitHeight, climateModels.Window.height - topMargin - bottomMargin)
                    padding: 1

                    contentItem: ListView {
                        clip: true
                        implicitHeight: contentHeight
                        model: climateModels.popup.visible ? climateModels.delegateModel : null
                        currentIndex: climateModels.highlightedIndex

                        ScrollIndicator.vertical: ScrollIndicator { }
                    }

                    background: Rectangle {
                        border.color: "#90BABAEE"
                        color: "#90BABAEE"
                        radius: 2
                    }
                }
            }
        }

        Item {
            id: checkWeatherbutton
            Layout.leftMargin: 15
            Layout.topMargin: -5
            implicitWidth: 150
            implicitHeight: 60

            Image {
                id: checkWeatherbuttonBackground
                anchors.fill: parent
                source: "../resources/check_weather_button.png"
                fillMode: Image.PreserveAspectFit
            }

            Text {
                id: checkWeatherbuttonText
                anchors.centerIn: parent
                text: qsTr("Check Weather!")
                color: Material.background
                font.family: "../resources/m5x7.ttf"
                font.pixelSize: 16
                antialiasing: false
                renderType: Text.NativeRendering
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    weather_components.update_current_status()
                }
            }
        }

        Item {
            id: backButton
            Layout.leftMargin: -10
            Layout.topMargin: 180

            implicitWidth: 30
            implicitHeight: 20

            Image {
                id: backButtonBackground
                anchors.fill: parent
                source: "../resources/back_button.png"
                fillMode: Image.PreserveAspectFit
            }

            MouseArea {
                anchors.fill: parent
                onClicked: backClicked()
            }
        }
    }

    ColumnLayout {
        Layout.preferredWidth: parent.width * 0.5
        Layout.preferredHeight: parent.height
        Layout.leftMargin: 220
        Layout.topMargin: 15

        Frame  {
            implicitWidth: 700
            implicitHeight: 650
            background: Rectangle {
                color: "#90BABAEE"
                opacity: 0.5
            }

            Image {
                id: displayCinnamorollExpression
                x: 70
                y: 135
                width: 300
                height: 320
                source: weather_components.cinnamoroll_source
                fillMode: Image.PreserveAspectFit
            }

            Rectangle {
                id: displayCinnamorollInfos
                width: parent.width - displayWeatherInfos.width
                height: 60
                x: 0
                y: 390
                color: "#dfe9fb"

                Text {
                    id: textDisplayCinnamorollMessage
                    anchors.fill: parent
                    anchors.margins: 8
                    color: Material.accent
                    font.bold: true
                    font.family: "../resources/m5x7.ttf"
                    font.pixelSize: 13
                    antialiasing: false
                    wrapMode: Text.Wrap
                    renderType: Text.NativeRendering
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    text: weather_components.cinnamoroll_message
                }
            }

            Rectangle {
                id: displayWeatherInfos
                width: 250
                height: displayCinnamorollExpression.height
                x: 430
                y: displayCinnamorollExpression.y
                color: Material.background
                opacity: 0.8

                Text {
                    id: textDisplayWeather
                    anchors.centerIn: parent
                    color: "white"
                    font.bold: true
                    font.family: "../resources/m5x7.ttf"
                    font.pixelSize: 13
                    antialiasing: false
                    wrapMode: Text.Wrap
                    renderType: Text.NativeRendering
                    text: weather_components.weather_message
                }
            }
        }
    }
}
