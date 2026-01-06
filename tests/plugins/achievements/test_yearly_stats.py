import datetime as dt
import logging
import os
import tempfile
from unittest import mock

import pytest

import octoprint.plugins.achievements
from octoprint.plugin import PluginSettings


@pytest.fixture()
def initialized_plugin():
    with tempfile.TemporaryDirectory() as basepath:
        plugin = octoprint.plugins.achievements.AchievementsPlugin()
        plugin._data_folder = basepath
        plugin._logger = logging.getLogger(
            "octoprint.plugins.achievements.AchievementsPlugin"
        )

        mocked_settings = mock.MagicMock()
        mocked_settings.get.return_value = None
        plugin._settings = PluginSettings(mocked_settings, plugin_key="achievements")

        yield plugin


@pytest.mark.time_machine(dt.datetime(2025, 12, 25))
def test_load_year(initialized_plugin):
    initialized_plugin._load_current_year_file()

    assert initialized_plugin._current_year_stats is not None
    assert initialized_plugin._current_year_stats.year == 2025
    assert os.path.exists(os.path.join(initialized_plugin._data_folder, "2025.json"))


@pytest.mark.time_machine(dt.datetime(2025, 12, 31))
def test_year_change(initialized_plugin, time_machine):
    initialized_plugin._load_current_year_file()

    assert initialized_plugin._current_year_stats.year == 2025

    initialized_plugin._current_year_stats.server_starts += 1

    time_machine.move_to(dt.datetime(2026, 1, 1))

    assert initialized_plugin._current_year_stats.server_starts == 0
    assert initialized_plugin._current_year_stats.year == 2026
    assert os.path.exists(os.path.join(initialized_plugin._data_folder, "2025.json"))
    assert os.path.exists(os.path.join(initialized_plugin._data_folder, "2026.json"))
