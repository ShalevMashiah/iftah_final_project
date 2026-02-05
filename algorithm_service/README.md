# **Project Name**

## **1. Service Overview**

- **Version:** [Current version number]
- **Author:** [Your name]


### **Badges**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)  [![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://www.docker.com/)  [![Kafka](https://img.shields.io/badge/Kafka-Integrated-yellow)](https://kafka.apache.org/)

### **Description**
  [Provide a brief description of what this service does and its main purpose]

## **2. Service Architecture**

### **Tech Stack/Framework:** 
This project was built using the following technologies: 
  - Kafka-python: Kafka producer for inter-service communication.

### **Dependencies/Features:**
  - Command Execution: Routes and executes commands from the client with Kafka integration for messaging.
  - Extensible Design: Implements the Factory pattern for modularity and scalability.

## **3. API Specifications**

### **http server:**

#### Commands - for all system commands

```http
GET /command/{state}/{status}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `state`      | `string` | **Required**. Current command that needed |
| `status`      | `string` | **Required**. Status to state (on/off) |

*Description*:
This endpoint is used to control various components in the system, such as turning lights on/off or activating ventilation.

for exmple: `GET /command/{blue_light}/{on}`

### **Kafka Topic:**
- **Topic Name:** [e.g., normalized-joystick-values]
- **Message Format:** [e.g., JSON]

#### Message Structure:
```json
{
  "key1": "value1",
  "key2": "value2"
}
```

[Provide any additional information about message handling if necessary]


## **4. Installation**

[Provide step-by-step installation instructions]

```bash
# Example installation steps
git clone [repository-url]
cd [project-directory]
pip install -r requirements.txt
```

## **5. Usage**

### **Run Command**
[Provide instructions on how to use the service]

```bash
# Example usage command
python3 src/main.py
```

### **Prerequisites**
To run this project, you will need to have the following installed:

- *Python 3.8+* 
- *Docker & Docker Compose* (recommended for containerized deployment)  
- *Git* (for cloning the repository)

Make sure to set up a `.env` file with the required environment variables (see **Environment Variables** section).

### **Environment Variables**

To run this project, you will need to add the following environment variables to your .env file or to environment section in this service on docker-compose.yml file.

`HTTP_SERVER_HOST=<http-server-host>`

`HTTP_SERVER_PORT=<http-server-port>`


## **6. Configuration**

[Describe any configuration steps or files needed]

## **7. Testing**

[Provide information on how to run tests]

```bash
# Example test command
pytest
```

## **8. Deployment**

[Provide information on how to deploy the service]

## **9. OS Restrictions**

[Provide information about features that are limited to specific operating systems, along with the required operating system and version]

## **10. Troubleshooting**

[Provide common issues and their solutions]

## **11. Documentation**
[Provide link to more document]

## **12. Future Plans**
[Provide future plans]