# API Endpoints

The staging API can be found at: `https://flare-portal.staging.torchbox.com/api/v1/`

## Starting an experiment

**Endpoint**

```
POST /api/v1/configuration/
```

**Payload**

```json
{
  "participant": "EXAMPLE.ABC123"
}
```

**Return**

```json
{
  "experiment": {
    "id": 6,
    "name": "Demo experiment",
    "trial_length": 10.0,
    "rating_delay": 1.0,
    "rating_scale_anchor_label_left": "Certain no scream",
    "rating_scale_anchor_label_center": "Uncertain",
    "rating_scale_anchor_label_right": "Certain scream"
  },
  "modules": [
    {
      "id": 7,
      "type": "FEAR_CONDITIONING",
      "config": {
        "phase": "habituation",
        "trials_per_stimulus": 12,
        "reinforcement_rate": 6,
        "generalisation_stimuli_enabled": false
      }
    },
    {
      "id": 8,
      "type": "FEAR_CONDITIONING",
      "config": {
        "phase": "habituation",
        "trials_per_stimulus": 0,
        "reinforcement_rate": 0,
        "generalisation_stimuli_enabled": false
      }
    }
  ]
}
```

## Sending experiment data

**Endpoint**

```
POST /api/v1/<module-data>/
```

`<module-data>` is `fear-conditioning-data`, `basic-info-data`, etc. It's the
slugified name of the data Django model.

**Payload**

```json
{
  "participant": "EXAMPLE.ABC123",
  "module": 7,
  "trial": 2,
  "rating": 5,
  "conditional_stimulus": "CSA",
  "unconditional_stimulus": true,
  "trial_started_at": "2020-12-07T14:00:00Z",
  "response_recorded_at": "2020-12-07T14:00:10Z",
  "volume_level": "0.57",
  "headphones": true
}
```

`participant` and `module` are always required. The other fields are based on
the `Data` model for the module type you're submitting data for.

**Return**

```json
{
  "id": 5,
  "participant": "EXAMPLE.ABC123",
  "trial": 2,
  "rating": 5,
  "conditional_stimulus": "CSA",
  "unconditional_stimulus": true,
  "trial_started_at": "2020-12-07T14:00:00Z",
  "response_recorded_at": "2020-12-07T14:00:10Z",
  "volume_level": "0.57",
  "headphones": true,
  "module": 7
}
```
