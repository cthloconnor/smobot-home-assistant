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
- PID-style sensors: `P`, `I`, `Kp`, `Ki`, `Kd`
- Device state sensor
- Operating state diagnostic sensor
- Probe status diagnostic sensor
- Raw payload diagnostic sensor
- Lid open binary sensor
- Grill setpoint number entity
- Manual refresh button
- DHCP discovery for devices advertising as `SMOBOT*`

## Repository Layout

- Integration code: `custom_components/smobot`

## Install

### HACS

1. Open HACS.
2. Go to `Integrations`.
3. Open the three-dot menu and choose `Custom repositories`.
4. Add `https://github.com/cthloconnor/smobot-home-assistant` as an `Integration`.
5. Search for `Smobot` in HACS and install it.
6. Restart Home Assistant.
7. Go to `Settings -> Devices & Services -> Add Integration`.
8. Search for `Smobot` and complete setup.

### Manual

1. Copy `custom_components/smobot` into your Home Assistant config directory.
2. Restart Home Assistant.
3. Go to `Settings -> Devices & Services -> Add Integration`.
4. Search for `Smobot`.
5. Enter the Smobot IP address on your local network.

## Notes

- Assumes the Smobot API is available at `http://<host>/ajax/`.
- Temperatures default to Fahrenheit.
- Diagnostic entities are disabled by default to keep the default dashboard cleaner.
- A diagnostic refresh button is included if you want to force an immediate poll.

## License

MIT
