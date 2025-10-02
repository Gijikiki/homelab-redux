#!/bin/bash

# Function to prompt for a variable
prompt_variable() {
  local var_name="$1"
  local prompt_message="$2"
  read -p "$prompt_message: " value
  echo "$value"
}

# Function to increment an IP address
increment_ip() {
  local ip="$1"
  local increment=${2:-1}  # Default increment is 1 if not provided

  # Convert IP to decimal
  ip_dec=$(printf "%d" $(echo "$ip" | awk -F. '{ print ($1 * 256^3) + ($2 * 256^2) + ($3 * 256) + $4 }'))

  # Increment the decimal value
  ip_dec=$((ip_dec + increment))

  # Check if the last octet exceeds 254
  last_octet=$((ip_dec & 255))
  if [ "$last_octet" -gt 254 ]; then
    echo "Error: IP address incremented beyond .254" >&2
    return 1
  fi

  # Convert back to dotted-quad format
  printf "%d.%d.%d.%d\n" $(( (ip_dec >> 24) & 255 )) $(( (ip_dec >> 16) & 255 )) $(( (ip_dec >> 8) & 255 )) $(( ip_dec & 255 ))
}

# Function to generate a list of IP addresses
generate_ip_list() {
  local start_ip="$1"
  local amt="$2"

  if ! [[ "$amt" =~ ^[0-9]+$ ]]; then
    echo "Error: Amount must be a positive integer." >&2
    return 1
  fi

  local current_ip="$start_ip"
  local ip_list=()

  for ((i = 0; i < amt; i++)); do
    ip_list+=("$current_ip")
    current_ip=$(increment_ip "$current_ip") || return 1
  done

  printf "%s\n" "${ip_list[@]}"
}

# Function to generate a list of strings with incremented numbers
generate_string_list() {
  local base_string="$1"
  local amt="$2"

  if ! [[ "$amt" =~ ^[0-9]+$ ]]; then
    echo "Error: Amount must be a positive integer." >&2
    return 1
  fi

  local result=()

  for ((i = 1; i <= amt; i++)); do
    result+=("${base_string}$(printf "%02d" $i)")
  done

  printf "%s\n" "${result[@]}"
}

# Function to create a list of host dictionaries
create_preseed_info() {
  local amt="$1"
  local base_hostname="$2"
  local start_ip="$3"
  local netmask="$4"
  local gateway="$5"

  if ! [[ "$amt" =~ ^[0-9]+$ ]]; then
    echo "Error: Amount must be a positive integer." >&2
    return 1
  fi

  local hostnames=( $(generate_string_list "$base_hostname" "$amt") )
  local ips=( $(generate_ip_list "$start_ip" "$amt") )
  PRESEED_INFO=()

  for ((i = 0; i < amt; i++)); do
    PRESEED_INFO+=("hostname=${hostnames[$i]} ip=${ips[$i]}")
  done

  printf "%s\n" "${PRESEED_INFO[@]}"
}

# Main function to handle prompts and confirmation
main_prompt() {
  while true; do
    echo "Please provide the following information:"

    # Example variables to prompt for
    local NUMBER_OF_HOSTS=$(prompt_variable "NUMBER_OF_HOSTS", "Enter how many servers")
    local HOSTNAME=$(prompt_variable "HOSTNAME BASENAME" "Enter the base hostname")
    local IP_ADDRESS=$(prompt_variable "FIRST IP_ADDRESS" "Enter the IP address")
    NETMASK=$(prompt_variable "NETMASK" "Enter the netmask")
    GATEWAY=$(prompt_variable "GATEWAY" "Enter the gateway")

    # Create Host List
    create_preseed_info $NUMBER_OF_HOSTS $HOSTNAME $IP_ADDRESS

    echo "\nSummary of your input:"
    echo "Number of hosts: $NUMBER_OF_HOSTS"
    echo "Host IPs: $IP_ADDRESS_LIST"
    echo "IP Address Start: $IP_ADDRESS"
    echo "Netmask: $NETMASK"
    echo "Gateway: $GATEWAY"

    # Confirm the input
    read -p "Is this information correct? (y/n/q): " confirmation

    case $confirmation in
      [Yy])
        echo "Confirmed. Proceeding with the installation."
        break
        ;;
      [Nn])
        echo "Restarting prompts."
        ;;
      [Qq])
        echo "Quitting installation."
        exit 1
        ;;
      *)
        echo "Invalid response. Please enter 'y', 'n', or 'q'."
        ;;
    esac
  done
}

# Execute the main prompt
main_prompt

