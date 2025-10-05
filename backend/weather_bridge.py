"""Bridge file to connect backend and qml."""

from datetime import datetime
from typing import List

from PySide6.QtCore import Property, QObject, Signal, Slot
from backend import weather_forecast

class WeatherBridge(QObject):
    """Bridge class to expose weather data to QML."""

    ip_message_changed = Signal()
    weather_message_changed = Signal()
    timezone_name_changed = Signal()
    live_local_time_changed = Signal()

    input_location_changed = Signal()
    selected_date_changed = Signal()
    weather_models_changed = Signal()
    est_input_date_changed = Signal()

    cinnamoroll_message_changed = Signal()
    cinnamoroll_source_changed = Signal()

    error_message = Signal(str)

    def __init__(self, parent: QObject = None) -> None:  # type: ignore
        """Initialize the WeatherBridge."""
        super().__init__(parent)
        self.weather_data = weather_forecast.WeatherData()
        self.update_current_status()

        self._daily_dates: List[str] = []

    def emit_error_message(self, message: str) -> None:
        """Emit error message signal."""
        self.error_message.emit(message)

    @Slot()
    def update_current_status(self) -> None:
        """Refresh the weather data every 1 minute."""
        try:
            self.weather_data.validation_and_live_update(self.emit_error_message)
            self.ip_message_changed.emit()
            self.weather_message_changed.emit()
            self.cinnamoroll_source_changed.emit()
            self.cinnamoroll_message_changed.emit()
        except Exception as e:
            self.emit_error_message(str(e))

    @Property(str, notify=est_input_date_changed)
    def est_input_date(self) -> str:
        """Getter."""
        return self.weather_data.est_input_date

    @est_input_date.setter  # type: ignore
    def est_input_date(self, value: str) -> None:
        """Setter."""
        self.weather_data.est_input_date = value
        self.est_input_date_changed.emit()

    @Property(str, notify=ip_message_changed)
    def ip_message(self) -> str:
        """Getter."""
        return self.weather_data.ip_message

    @ip_message.setter  # type: ignore
    def ip_message(self, value: str) -> None:
        """Setter."""
        self.weather_data.ip_message = value
        self.ip_message_changed.emit()

    @Property(str, notify=weather_message_changed)
    def weather_message(self) -> str:
        """Getter."""
        return self.weather_data.weather_message

    @weather_message.setter  # type: ignore
    def weather_message(self, value: str) -> None:
        """Setter."""
        self.weather_data.weather_message = value
        self.weather_message_changed.emit()

    @Property(str, notify=timezone_name_changed)
    def timezone_name(self) -> str:
        """Getter."""
        return self.weather_data.timezone_name

    @timezone_name.setter  # type: ignore
    def timezone_name(self, value: str) -> None:
        """Setter."""
        self.weather_data.timezone_name = value
        self.timezone_name_changed.emit()

    @Property(str, notify=live_local_time_changed)
    def live_local_time(self) -> str:
        current_time = self.weather_data.get_live_local_time()
        return current_time.strftime("%H:%M:%S")
    
    @Slot()
    def tick_local_time(self) -> None:
        self.live_local_time_changed.emit()

    @Property(str, notify=input_location_changed)
    def input_location(self) -> str:
        """Getter."""
        return self.weather_data.input_location

    @input_location.setter  # type: ignore
    def input_location(self, value: str) -> None:
        """Setter."""
        self.weather_data.input_location = value
        self.input_location_changed.emit()

    @Property(str, notify=selected_date_changed)
    def selected_date(self) -> str:
        """Getter."""
        return self.weather_data.selected_date

    @selected_date.setter  # type: ignore
    def selected_date(self, value: str) -> None:
        """Setter."""
        self.weather_data.selected_date = value
        self.selected_date_changed.emit()

    @Slot(result=list)
    def choose_forecast_dates(self) -> list[str]:
        """Expose forecast dates to QML."""
        returned_weather = self.weather_data.get_weather_by_date(
            self.emit_error_message
        )
        if returned_weather:
            self._daily_dates = returned_weather[1]
        return self._daily_dates

    @Property(str, notify=weather_models_changed)
    def weather_models(self) -> str:
        """Getter."""
        return weather_forecast.ui_name_for_api(
            self.weather_data.weather_models
        )

    @weather_models.setter  # type: ignore
    def weather_models(self, value: str) -> None:
        """Setter."""
        api_model = weather_forecast.api_model_for_ui(value)
        self.weather_data.weather_models = api_model
        self.weather_models_changed.emit()

    @Property(list, constant=True)
    def model_map(self) -> list[str]:
        """Expose MODEL_MAP to QML as a dictionary."""
        return weather_forecast.model_ui_list()
    
    @Property(str, notify=cinnamoroll_message_changed)
    def cinnamoroll_message(self) -> str:
        """Getter."""
        return self.weather_data.cinnamoroll_message

    @cinnamoroll_message.setter  # type: ignore
    def cinnamoroll_message(self, value: str) -> None:
        """Setter."""
        self.weather_data.cinnamoroll_message = value
        self.cinnamoroll_message_changed.emit()

    @Property(str, notify=cinnamoroll_source_changed)
    def cinnamoroll_source(self) -> str:
        """Getter."""
        return self.weather_data.cinnamoroll_source

    @cinnamoroll_source.setter  # type: ignore
    def cinnamoroll_source(self, value: str) -> None:
        """Setter."""
        self.weather_data.cinnamoroll_source = value
        self.cinnamoroll_source_changed.emit()
