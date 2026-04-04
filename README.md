# Smobot Home Assistant Custom Integration

This custom integration talks directly to a local Smobot unit over its HTTP API.

It was based on the public `smobot` Python package at:

- https://github.com/eavanvalkenburg/smobot

## What it exposes

- Grill temperature sensor
- Food probe 1 sensor
- Food probe 2 sensor
- Grill climate control
- Damper state sensor
- Damper mode sensor
- Cook time sensor
- Error sensor
- PID sensors (`P`, `I`, `D`, `Kp`, `Ki`, `Kd`)
- Device state sensor
- Lid open binary sensor
- Grill setpoint number control

## Install

1. Copy `/Users/Cathal1/Documents/New project/smobot-home-assistant/custom_components/smobot` into your Home Assistant config directory under `custom_components/smobot`.
2. Restart Home Assistant.
3. Go to `Settings -> Devices & Services -> Add Integration`.
4. Search for `Smobot`.
5. Enter the Smobot IP address or hostname on your local network.

DHCP discovery is also included for devices that announce themselves as `SMOBOT*`.

## Notes

- This integration assumes the Smobot local API is available at `http://<host>/ajax/`.
- Temperatures default to Fahrenheit, but you can change the unit reported by the device and setpoint safety limits in the integration options.
- Advanced diagnostic entities are created disabled by default to keep the default dashboard cleaner.
