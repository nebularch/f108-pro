#!/usr/bin/env python3

import os
import shutil
import subprocess
import threading
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib


def find_backend():
    """Locate the f108-pro executable."""

    candidates = []

    configured = os.environ.get("F108_PRO_BIN")
    if configured:
        candidates.append(Path(configured).expanduser())

    installed = shutil.which("f108-pro")
    if installed:
        candidates.append(Path(installed))

    project_root = Path(__file__).resolve().parents[1]
    candidates.extend([
        project_root / "build" / "f108-pro",
        project_root / "f108-pro",
    ])

    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)

    return None


MODES = [
    ("Off", "off"),
    ("Static", "static"),
    ("Single On", "singleon"),
    ("Single Off", "singleoff"),
    ("Glittering", "glittering"),
    ("Falling", "falling"),
    ("Colourful", "colourful"),
    ("Breath", "breath"),
    ("Spectrum", "spectrum"),
    ("Outward", "outward"),
    ("Scrolling", "scrolling"),
    ("Rolling", "rolling"),
    ("Rotating", "rotating"),
    ("Explode", "explode"),
    ("Launch", "launch"),
    ("Ripples", "ripples"),
    ("Flowing", "flowing"),
    ("Pulsating", "pulsating"),
    ("Tilt", "tilt"),
    ("Shuttle", "shuttle"),
]


DIRECTION_MODES = {
    "scrolling",
    "rolling",
    "rotating",
    "flowing",
    "tilt",
}


RAINBOW_MODES = {
    "colourful",
    "spectrum",
}


class F108GUI(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id="com.noir.AULAF108Pro"
        )

        self.backend = find_backend()
        self.window = None
        self.status = None
        self.mode = None
        self.color = None
        self.brightness = None
        self.speed = None
        self.direction = None

    # ---------------------------------------------------------
    # APPLICATION
    # ---------------------------------------------------------

    def do_activate(self):
        if self.window is None:
            self.build_ui()

        self.window.present()

    # ---------------------------------------------------------
    # BUILD UI
    # ---------------------------------------------------------

    def build_ui(self):

        self.window = Gtk.ApplicationWindow(
            application=self,
            title="AULA F108 PRO",
            default_width=520,
            default_height=650,
        )

        self.window.set_resizable(False)

        main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
        )

        main.set_margin_top(24)
        main.set_margin_bottom(24)
        main.set_margin_start(28)
        main.set_margin_end(28)

        self.window.set_child(main)

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        title = Gtk.Label()

        title.set_markup(
            '<span size="xx-large" weight="bold">'
            'AULA F108 PRO'
            '</span>'
        )

        main.append(title)

        subtitle = Gtk.Label(
            label="Linux Control Center"
        )

        subtitle.add_css_class("dim-label")

        main.append(subtitle)

        # -----------------------------------------------------
        # LIGHTING MODE
        # -----------------------------------------------------

        mode_label = Gtk.Label(
            label="Lighting Mode",
            xalign=0,
        )

        mode_label.add_css_class("heading")

        main.append(mode_label)

        self.mode = Gtk.DropDown.new_from_strings(
            [name for name, _ in MODES]
        )

        # Default to Static
        self.mode.set_selected(1)

        self.mode.connect(
            "notify::selected",
            self.on_mode_changed,
        )

        main.append(self.mode)

        # -----------------------------------------------------
        # COLOR
        # -----------------------------------------------------

        color_label = Gtk.Label(
            label="Color",
            xalign=0,
        )

        color_label.add_css_class("heading")

        main.append(color_label)

        color_dialog = Gtk.ColorDialog()

        self.color = Gtk.ColorDialogButton(
            dialog=color_dialog
        )

        rgba = Gdk.RGBA()
        rgba.parse("#00ffff")

        self.color.set_rgba(rgba)

        main.append(self.color)

        # -----------------------------------------------------
        # BRIGHTNESS
        # -----------------------------------------------------

        brightness_label = Gtk.Label(
            label="Brightness",
            xalign=0,
        )

        brightness_label.add_css_class("heading")

        main.append(brightness_label)

        self.brightness = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            5,
            1,
        )

        self.brightness.set_value(5)
        self.brightness.set_draw_value(True)
        self.brightness.set_hexpand(True)

        main.append(self.brightness)

        # -----------------------------------------------------
        # SPEED
        # -----------------------------------------------------

        speed_label = Gtk.Label(
            label="Animation Speed",
            xalign=0,
        )

        speed_label.add_css_class("heading")

        main.append(speed_label)

        self.speed = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0,
            5,
            1,
        )

        self.speed.set_value(5)
        self.speed.set_draw_value(True)
        self.speed.set_hexpand(True)

        main.append(self.speed)

        # -----------------------------------------------------
        # DIRECTION
        # -----------------------------------------------------

        direction_label = Gtk.Label(
            label="Direction",
            xalign=0,
        )

        direction_label.add_css_class("heading")

        main.append(direction_label)

        self.direction = Gtk.DropDown.new_from_strings([
            "Forward",
            "Reverse",
        ])

        self.direction.set_selected(0)
        self.direction.set_sensitive(False)

        main.append(self.direction)

        # -----------------------------------------------------
        # APPLY BUTTON
        # -----------------------------------------------------

        self.apply_button = Gtk.Button(
            label="Apply Lighting"
        )

        self.apply_button.add_css_class(
            "suggested-action"
        )

        self.apply_button.set_margin_top(8)

        self.apply_button.connect(
            "clicked",
            self.apply_lighting,
        )

        main.append(self.apply_button)

        # -----------------------------------------------------
        # QUICK BUTTONS
        # -----------------------------------------------------

        quick_buttons = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )

        quick_buttons.set_homogeneous(True)

        spectrum_button = Gtk.Button(
            label="🌈 Spectrum"
        )

        spectrum_button.connect(
            "clicked",
            self.enable_spectrum,
        )

        off_button = Gtk.Button(
            label="⛔ Lights Off"
        )

        off_button.connect(
            "clicked",
            self.turn_off,
        )

        quick_buttons.append(spectrum_button)
        quick_buttons.append(off_button)

        main.append(quick_buttons)

        # -----------------------------------------------------
        # CLOCK
        # -----------------------------------------------------

        clock_button = Gtk.Button(
            label="🕐 Sync LCD Clock"
        )

        clock_button.set_margin_top(8)

        clock_button.connect(
            "clicked",
            self.sync_clock,
        )

        main.append(clock_button)

        # -----------------------------------------------------
        # SEPARATOR
        # -----------------------------------------------------

        separator = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL
        )

        separator.set_margin_top(8)
        separator.set_margin_bottom(4)

        main.append(separator)

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        self.status = Gtk.Label(
            label="Ready",
            xalign=0,
        )

        self.status.add_css_class("dim-label")

        main.append(self.status)

        # Update controls for initial mode
        self.update_controls()

    # ---------------------------------------------------------
    # MODE CHANGED
    # ---------------------------------------------------------

    def on_mode_changed(self, dropdown, param):

        self.update_controls()

    # ---------------------------------------------------------
    # UPDATE CONTROLS
    # ---------------------------------------------------------

    def update_controls(self):

        if self.mode is None:
            return

        index = self.mode.get_selected()

        if index >= len(MODES):
            return

        mode = MODES[index][1]

        is_off = mode == "off"
        is_rainbow = mode in RAINBOW_MODES
        has_direction = mode in DIRECTION_MODES

        self.color.set_sensitive(
            not is_off and not is_rainbow
        )

        self.brightness.set_sensitive(
            not is_off
        )

        self.speed.set_sensitive(
            not is_off and mode != "static"
        )

        self.direction.set_sensitive(
            has_direction
        )

    # ---------------------------------------------------------
    # GET RGB
    # ---------------------------------------------------------

    def get_rgb(self):

        rgba = self.color.get_rgba()

        red = round(rgba.red * 255)
        green = round(rgba.green * 255)
        blue = round(rgba.blue * 255)

        return red, green, blue

    # ---------------------------------------------------------
    # RUN COMMAND
    # ---------------------------------------------------------

    def run_command(self, command, success_message):

        if not self.backend:
            self.set_status(
                "Backend not found. Install f108-pro or set F108_PRO_BIN."
            )
            return

        def worker():

            try:

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:

                    GLib.idle_add(
                        self.set_status,
                        success_message,
                    )

                else:

                    error = result.stderr.strip()

                    if not error:
                        error = "Command failed."

                    GLib.idle_add(
                        self.set_status,
                        f"Error: {error}",
                    )

            except FileNotFoundError:

                GLib.idle_add(
                    self.set_status,
                    f"Could not execute backend: {command[0]}",
                )

            except Exception as error:

                GLib.idle_add(
                    self.set_status,
                    f"Error: {error}",
                )

        thread = threading.Thread(
            target=worker,
            daemon=True,
        )

        thread.start()

    # ---------------------------------------------------------
    # APPLY LIGHTING
    # ---------------------------------------------------------

    def apply_lighting(self, button):

        index = self.mode.get_selected()

        if index >= len(MODES):
            return

        mode = MODES[index][1]

        # Off
        if mode == "off":

            self.turn_off(button)
            return

        brightness = int(
            self.brightness.get_value()
        )

        speed = int(
            self.speed.get_value()
        )

        command = [
            self.backend,
            "light",
            mode,
            str(brightness),
            str(speed),
        ]

        # Normal color modes
        if mode not in RAINBOW_MODES:

            red, green, blue = self.get_rgb()

            command.extend([
                str(red),
                str(green),
                str(blue),
            ])

        # Directional modes
        if mode in DIRECTION_MODES:

            direction = str(self.direction.get_selected())

            command.extend([
                "-d",
                direction,
            ])

        self.set_status("Applying lighting...")

        self.run_command(
            command,
            "✓ Lighting applied",
        )

    # ---------------------------------------------------------
    # SPECTRUM
    # ---------------------------------------------------------

    def enable_spectrum(self, button):

        self.set_status(
            "Switching to Spectrum..."
        )

        self.run_command(
            [
                self.backend,
                "light",
                "spectrum",
            ],
            "✓ Spectrum enabled",
        )

    # ---------------------------------------------------------
    # LIGHTS OFF
    # ---------------------------------------------------------

    def turn_off(self, button):

        self.set_status(
            "Turning lights off..."
        )

        self.run_command(
            [
                self.backend,
                "off",
            ],
            "✓ Lighting turned off",
        )

    # ---------------------------------------------------------
    # CLOCK
    # ---------------------------------------------------------

    def sync_clock(self, button):

        self.set_status(
            "Synchronizing LCD clock..."
        )

        self.run_command(
            [
                self.backend,
                "clock",
            ],
            "✓ LCD clock synchronized",
        )

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def set_status(self, message):

        if self.status is not None:
            self.status.set_text(message)

        return False


def main():

    app = F108GUI()

    return app.run(None)


if __name__ == "__main__":
    raise SystemExit(main())
