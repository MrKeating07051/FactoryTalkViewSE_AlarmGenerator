import xml.etree.ElementTree as ET
import xml.dom.minidom
import re
from datetime import datetime
import os
import json

def load_config():
    config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    # Check if config.json exists
    if not os.path.exists(config_file_path):
        print(f"Warning: '{config_file_path}' does not exist.")
        input("Press any key to continue without the configuration file...")  # Pause and wait for the user
        return None  # Return None if the config doesn't exist, so defaults can be used
    else:
        with open(config_file_path, "r") as f:
            config = json.load(f)
            print(f"Config file: '{config_file_path}' loaded successfully.")
            print("Make sure to change the config file to suit the needs of your PLC program! \n")
        return config

def sanitize_name(name):
    # Remove any characters that are not alphabetic, numeric, space, or underscore
    sanitized = re.sub(r'[^a-zA-Z0-9 _]', '', name)
    
    # Ensure the name doesn't start with a space or underscore
    if sanitized and (sanitized[0] == ' ' or sanitized[0] == '_'):
        sanitized = sanitized[1:]

    # Limit the name to 200 characters
    sanitized = sanitized[:200]
    
    return sanitized

def create_alarm_xml(device, original_alarm, area, path, custom_alarm_name, message, config):
    # Sanitize the original alarm name
    original_alarm = sanitize_name(original_alarm)

    # Create XML structure
    ft_alarm_element = ET.Element("FTAlarmElement", {
        "name": f"{device} {custom_alarm_name}",
        "inuse": "Yes",
        "latched": "false",
        "ackRequired": "true",
        "style": "Discrete"
    })

    discrete_element = ET.SubElement(ft_alarm_element, "DiscreteElement")
    
    # Use the original alarm name for the FTAlarmElement DataItem and Severity
    ET.SubElement(discrete_element, "DataItem").text = f"{area}{path}{device}{config['tag_alm_prefix']}{original_alarm}"
    ET.SubElement(discrete_element, "Style").text = "DiscreteTrue"
    
    # Use the tag-defined alarm severity if configured
    if config["use_tag_severity"]:
        ET.SubElement(discrete_element, "Severity").text = f"{area}{path}{device}{config['tag_cfg_prefix']}{original_alarm}Severity"
    else:
        ET.SubElement(discrete_element, "Severity").text = input(f"Enter severity level for alarm '{custom_alarm_name}'\n0-250 = Low\n251-500 = Medium\n501-750 = High\n751-1000 = Urgent\n: ")

    ET.SubElement(discrete_element, "DelayInterval").text = "0"
    ET.SubElement(discrete_element, "EnableTag").text = "false"
    ET.SubElement(discrete_element, "UserData").text = ""
    ET.SubElement(discrete_element, "RSVCmd").text = ""
    ET.SubElement(discrete_element, "AlarmClass").text = ""
    ET.SubElement(discrete_element, "GroupID").text = config["default_group_id"]

    # HandshakeTags - Use the original alarm name here too, if enabled by config
    if config["use_handshake_tags"]:
        handshake_tags = ET.SubElement(discrete_element, "HandshakeTags")
        if config["handshake_inalarm"]:
            ET.SubElement(handshake_tags, "InAlarmDataItem").text = f"{area}{path}{device}{config['tag_sts_prefix']}{original_alarm}"
        else:
            ET.SubElement(handshake_tags, "InAlarmDataItem").text = ""
        if config["handshake_disabled"]:
            ET.SubElement(handshake_tags, "DisabledDataItem").text = f"{area}{path}{device}{config['tag_sts_prefix']}{original_alarm}Disabled"
        else:
            ET.SubElement(handshake_tags, "DisabledDataItem").text = ""
        if config["handshake_acked"]:
            ET.SubElement(handshake_tags, "AckedDataItem").text = f"{area}{path}{device}{config['tag_sts_prefix']}{original_alarm}Acked"
        else:
            ET.SubElement(handshake_tags, "AckedDataItem").text = ""
        if config["handshake_suppressed"]:
            ET.SubElement(handshake_tags, "SuppressedDataItem").text = f"{area}{path}{device}{config['tag_sts_prefix']}{original_alarm}Suppressed"
        else:
            ET.SubElement(handshake_tags, "SuppressedDataItem").text = ""
        if config["handshake_shelved"]:
            ET.SubElement(handshake_tags, "ShelvedDataItem").text = f"{area}{path}{device}{config['tag_sts_prefix']}{original_alarm}Shelved"
        else:
            ET.SubElement(handshake_tags, "ShelvedDataItem").text = ""

    # Remote commands
    ET.SubElement(discrete_element, "RemoteAckAllDataItem", AutoReset="false")
    ET.SubElement(discrete_element, "RemoteDisableDataItem", AutoReset="false")
    ET.SubElement(discrete_element, "RemoteEnableDataItem", AutoReset="false")
    ET.SubElement(discrete_element, "RemoteSuppressDataItem", AutoReset="false")
    ET.SubElement(discrete_element, "RemoteUnSuppressDataItem", AutoReset="false")
    ET.SubElement(discrete_element, "RemoteShelveAllDataItem", AutoReset="false")
    ET.SubElement(discrete_element, "RemoteUnShelveDataItem", AutoReset="false")
    ET.SubElement(discrete_element, "RemoteShelveDuration").text = ""

    # Add MessageID and Params (as per the provided structure)
    ET.SubElement(discrete_element, "MessageID").text = "0"
    params = ET.SubElement(discrete_element, "Params")
    param = ET.SubElement(params, "Param", key="Tag1")
    param.text = f"{area}{path}{device}.Cfg_Tag"

    # Prepare polling line with <Tag> elements - use original alarm name here
    polling_line = f"""
<Tag>{area}{path}{device}{config['tag_alm_prefix']}{original_alarm}</Tag>
<Tag>{area}{path}{device}{config['tag_cfg_prefix']}Tag</Tag>
<Tag>{area}{path}{device}{config['tag_cfg_prefix']}{original_alarm}Severity</Tag>
"""

    # Prepare message if provided
    message_output = ""
    if message:
        message_output = f"""
<Message id="0">
    <Msgs>
        <Msg xml:lang="en-US">/*S:0 %Tag1*/ {custom_alarm_name} - {message}</Msg>
    </Msgs>
</Message>
"""

    return polling_line, message_output, ET.tostring(ft_alarm_element, 'utf-8')

def main():
    print("FactoryTalk View Site Edition XML Alarm Generator\nVersion 1\nCreated by Seth Thompson\n")
    # Load configuration from file
    config = load_config()
    
    while True:
        # Use default area and path from config
        area = config["default_data_area"] if config else "/Area::"
        path = config["default_plc_path"] if config else "[CLX]"

        # Enter device name
        device = input("Enter Device Name (e.g., DCV901212): ")

        # Create list to hold alarms
        alarms = []

        # Loop to enter alarms
        while True:
            # Enter the first alarm name
            original_alarm = input("Enter Alarm as entered on PLC (e.g., FullStall): ")

            if not original_alarm:
                break  # Exit if the user presses enter without typing anything

            # Enter custom alarm name for the first alarm
            custom_alarm_name = input(f"Enter human-readable alarm name for '{original_alarm}' (or press Enter to skip): ")
            if custom_alarm_name:
                custom_alarm_name = sanitize_name(custom_alarm_name)
            else:
                custom_alarm_name = original_alarm

            # Prompt for message generation
            generate_message = input(f"Do you want to generate a message for '{custom_alarm_name}'? (Y/N): ").strip().upper()
            message = ""
            if generate_message == "Y":
                message = input("Enter message for alarm: ")

            # Append the alarm data to the list
            alarms.append((original_alarm, custom_alarm_name, message))

            # Prompt to enter additional alarms or finish
            add_more = input("Do you want to add another alarm? (Y/N): ").strip().upper()
            if add_more != "Y":
                print("\n")
                break  # Exit loop if no more alarms to add

        # Get current date and time
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the output text file path (in the same directory as the script)
        script_directory = os.path.dirname(__file__)
        output_file_name = f"{device}_{now.strftime('%Y%m%d_%H%M')}.txt"
        output_file_path = os.path.join(script_directory, output_file_name)

        # Open the file in append mode to prevent overwriting
        with open(output_file_path, "a") as output_file:
            for alarm in alarms:
                original_alarm, custom_alarm_name, message = alarm
                polling_info, message_output, xml_output = create_alarm_xml(
                    device, original_alarm, area, path, custom_alarm_name, message, config)

                # Pretty format the output
                output_file.write(f"\nGenerated on {current_time}\n\n")
                output_file.write(f"======= Alarm '{custom_alarm_name}' for device '{device}' ============================\n\nPolling interval tags:\n{polling_info}\n")

                if message_output:
                    output_file.write(f"Generated Message:\n{message_output}\n")
                
                output_file.write(f"Generated Alarm Data:\n\n")
                # Pretty-print the XML string
                output_file.write(xml.dom.minidom.parseString(xml_output).toprettyxml(indent="  "))
                output_file.write(f"\n======= End of Alarm '{custom_alarm_name}' ============================\n\n")

            print(f"Alarm data has been written to: {output_file_path}\n")

        # Prompt to create another alarm set
        create_another = input("Do you want to create another alarm set? (Y/N): ").strip().upper()
        if create_another != "Y":
            print("Exiting the program.")
            break

if __name__ == "__main__":
    main()
