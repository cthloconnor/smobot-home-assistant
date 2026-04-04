# Smobot Home Assistant

Custom Home Assistant integration for a local Smobot controller.

This integration talks directly to the Smobot HTTP API and exposes the cooker state as native Home Assistant entities.

Based on:
- [eavanvalkenburg/smobot](https://github.com/eavanvalkenburg/smobot)

## Features

- Grill temperature sensor
- Food probe 1 sensor
- Food probe 2 sensor
- Grill climate control
- Damper state sensor
- Damper mode sensor
- Cook time sensor
- Error sensor
- PID sensors: `P`, `I`, `D`, `Kp`, `Ki`, `Kd`
- Device state sensor
- Lid open binary sensor
- Grill setpoint number entity
- DHCP discovery for devices advertising as `SMOBOT*`

## Repository Layout

- Integration code: `custom_components/smobot`

## Install

1. Copy `custom_components/smobot` into your Home Assistant config directory.
2. Restart Home Assistant.
3. Go to `Settings -> Devices & Services -> Add Integration`.
4. Search for `Smobot`.
5. Enter the Smobot IP address or hostname on your local network.

## Notes

- Assumes the Smobot API is available at `http://<host>/ajax/`.
- Temperatures default to Fahrenheit.
- Diagnostic entities are disabled by default to keep the default dashboard cleaner.

## License

MIT
