# Pyroscope for Home Assistant

A Home Assistant custom integration that continuously profiles Home Assistant Core with the
[Pyroscope Python SDK](https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/python/)
and sends the profiles to a Pyroscope server or Grafana Cloud Profiles. Use it to see which
integrations, automations and templates spend Home Assistant's CPU, without capturing a profile by
hand.

The SDK samples Home Assistant's own Python stacks from inside the process and needs no kernel
eBPF support, so it is an option on Home Assistant OS, whose kernel lacks the syscall tracepoints
that eBPF profilers need.

## Install

1. In HACS, open the menu, choose **Custom repositories**, and add
   `https://github.com/tomwilkie/ha-pyroscope` with the type **Integration**.
2. Install **Pyroscope** from HACS and restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and choose **Pyroscope**.

Home Assistant installs the `pyroscope-io` package into `/config/deps` on first setup, so it
survives Home Assistant updates.

## Configure

| Field | Grafana Cloud value |
|---|---|
| Server URL | The URL on your stack's **Profiles** details page |
| Username | The Profiles instance ID |
| Password or token | An access policy token with the `profiles:write` scope |
| Service name | Sent as `service_name`. Defaults to `homeassistant` |

For a self-hosted Pyroscope server without auth, enter its URL, for example
`http://pyroscope.local:4040`, and leave the username and password empty.

The setup form checks only that the URL is well formed. Bad credentials show up as upload errors
in the Home Assistant log.

Under **Configure** on the integration you can change the following options. Saving restarts the
profiler.

| Option | Default | Effect |
|---|---|---|
| Sample rate | 100 Hz | CPU samples per second. Lower it to reduce overhead |
| Memory profiling | Off | Also sends allocation profiles, at extra cost |

Only one entry is allowed, because the SDK profiles the whole process.

## Query

Every profile carries `service_name` and an `ha_version` tag, so you can compare releases. In
Grafana, open **Explore → Profiles** or Grafana Profiles Drilldown and select
`{service_name="homeassistant"}`.

## Overhead

The SDK samples from a native thread. Its overhead has not been measured yet, on any hardware.
If Home Assistant's CPU rises noticeably, lower the sample rate.

## Licence

Apache 2.0. See [LICENSE](LICENSE).
