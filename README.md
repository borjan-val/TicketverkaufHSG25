# Ticket Sale System for HSG School Party 2025

This project is a dockerized web application for managing ticket sales for the HSG school party in 2025. It allows administrators to create events, manage tickets, and track sales, while attendees can conveniently purchase tickets online.

## Project Overview

The system provides an intuitive user interface for ticket sales and management. It is based on the Flask web framework and utilizes a PostgreSQL database for data storage. Furthermore, it is containerized with docker to allow for safe and easy deployment. Its key features include:

- Creating and managing events
- Online ticket sales (local)
- Participant data management
- Generating sales reports

### Useful Features

This system simplifies the ticket sale process for events, reduces administrative effort, and provides attendees with a convenient way to purchase tickets online.

While designed for school parties, it can be repurposed for other events as it primarily facilitates in-person ticket sales.

---

## Deployment

1. Make sure Docker 20.10 or above is installed on your host and you have a PostgreSQL database set up and ready

## Development

> **IMPORTANT NOTE:** DO NOT use the web app running from your development container for deployment. The development version uses default credentials to simplify testing and poses a serious security risk if used in production. Furthermore, you may be risking data loss by using the testing database included in the DevContainer. If you want to deploy this application, please check the [Deployment section](#deployment) above.

1. Make sure you are using VSCode with the DevContainers extension installed or any other DevContainers-compatible code editor
2. Clone the repository
3. Open the repository working tree in your DevContainers compatible code editor
4. If you are prompted to do so, select "Reopen in Container" (VSCode-specific)
5. **You're all set up!** Thanks to the power of cloud-native development using DevContainers, you now have everything you need to get started developing.

> **Note:** Run all following commands _inside_ your DevContainer, e.g. using the terminal within VSCode when VSCode is connected to the DevContainer

The included DevContainer conviently provides aliases for quickly building, running and stopping the web app docker container. Simply use
```bash
build-ticketverkauf-dev # Rebuild the web app with your changes applied
run-ticketverkauf-dev   # Run the web app from the latest build
stop-ticketverkauf-dev  # Stop the running web app
```
By default, the development web app will be accessible on port 8080 on your host. If you'd like to reconfigure this, you can change it in `.devcontainer/devcontainer.json`.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure that you run tests and update the documentation accordingly. For instructions to set up your development environment, please refer to 

---

### License

This project is licensed under the [GNU General Public License](LICENSE).

---

### Contact

If you have any questions or suggestions, please create a discussion in the repository.

**Thank you! 😊**
