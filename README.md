# FactoryTalk View Site Edition XML Alarm Generator

## Overview
This Python script generates FactoryTalk View Site Edition (SE) XML alarm data based on input for devices and alarms. It creates XML alarms for devices connected to a PLC and generates a corresponding polling line and alarm messages. The output is saved in a text file that includes both human-readable alarm descriptions and well-structured XML data.

### Key Features:
- **Load Configuration**: Loads configuration settings from `config.json`.
- **Device and Alarm Input**: Prompts for device names, alarm names, and optionally custom alarm names and messages.
- **XML Alarm Generation**: Creates an XML structure for each alarm with the option to include a severity level, handshake tags, and remote commands.
- **Message Generation**: Optionally generates a custom message for each alarm.
- **Output File**: Saves the generated alarm data (both polling information and formatted XML) in a `.txt` file with a timestamp in its name.

---

## Installation

### Prerequisites:
- Python 3.6 or higher
- Required libraries:
    - `xml.etree.ElementTree` (standard library)
    - `xml.dom.minidom` (standard library)
    - `re` (standard library)
    - `datetime` (standard library)
    - `os` (standard library)
    - `json` (standard library)

To install Python and the required libraries, use:

```bash
pip install python
```

---

## Configuration

Create a `config.json` file in the same directory as the script with the following structure:

```json
{
    "default_data_area": "/Area::",
    "default_plc_path": "[CLX]",
    "tag_alm_prefix": "Alm_",
    "tag_cfg_prefix": "Cfg_",
    "tag_sts_prefix": "Sts_",
    "default_group_id": "1",
    "use_tag_severity": true,
    "use_handshake_tags": true,
    "handshake_inalarm": true,
    "handshake_disabled": true,
    "handshake_acked": true,
    "handshake_suppressed": true,
    "handshake_shelved": true
}
```

### Configuration Options:
- **default_data_area**: Default area in which alarms are defined.
- **default_plc_path**: Path to the PLC system.
- **tag_alm_prefix**: Prefix used for alarm tags.
- **tag_cfg_prefix**: Prefix used for configuration tags.
- **tag_sts_prefix**: Prefix used for status tags.
- **default_group_id**: Default group ID used for alarms.
- **use_tag_severity**: Whether to use the configured severity tags.
- **use_handshake_tags**: Whether to include handshake tags (e.g., InAlarm, Disabled, etc.).
- **handshake_inalarm, handshake_disabled, etc.**: Boolean values to define if the respective handshake tags should be used.

---

## Usage

1. Run the script:
   ```bash
   python alarm_generator.py
   ```

2. The program will load the configuration file (if present) and ask you to input:
   - Device name
   - Alarm name(s) as defined in the PLC
   - Custom human-readable alarm name(s) (optional)
   - Severity level for each alarm (if not using tag-based severity)
   - Messages for alarms (optional)

3. After inputting the alarms, the program will save the generated alarm data into a `.txt` file in the same directory as the script.

4. The output will include:
   - Polling information for each alarm
   - Generated XML for each alarm
   - Any generated messages

5. After completing, the script will ask if you want to generate another alarm set.

---

## Example Output

A generated might look like this:

```
Generated on 2024-10-18 12:30:45

======= Alarm 'FullStall' for device 'DCV901212' ============================

Polling interval tags:
<Tag>/Area::[CLX]DCV901212.Alm_FullStall</Tag>
<Tag>/Area::[CLX]DCV901212.Cfg_Tag</Tag>
<Tag>/Area::[CLX]DCV901212.Cfg_FullStallSeverity</Tag>

Generated Message:
<Message id="0">
    <Msgs>
        <Msg xml:lang="en-US">/*S:0 %Tag1*/ Full Stall - Equipment is in a full stall state</Msg>
    </Msgs>
</Message>

Generated Alarm Data:

<FTAlarmElement name="DCV901212 Full Stall" inuse="Yes" latched="false" ackRequired="true" style="Discrete">
  <DiscreteElement>
    <DataItem>/Area::[CLX]DCV901212.Alm_FullStall</DataItem>
    <Style>DiscreteTrue</Style>
    <Severity>/Area::[CLX]DCV901212.Cfg_FullStallSeverity</Severity>
    <DelayInterval>0</DelayInterval>
    <EnableTag>false</EnableTag>
    <UserData></UserData>
    <RSVCmd></RSVCmd>
    <AlarmClass></AlarmClass>
    <GroupID>1</GroupID>
  </DiscreteElement>
</FTAlarmElement>

======= End of Alarm 'FullStall' ============================
```

## To-do

- Create ability to write directly to FT View SE alarm export data and automatically detect existing alarm areas instead of manual copy/paste
- Create analog alarms (maybe)

---
