# MALIK-AI

**Malik AI** is a cloud-native AI application that delivers conversational responses powered by **OpenAI** and deployed on **AWS ECS (Fargate)** using reusable, production-ready infrastructure.

This project demonstrates **modern DevOps, security-first infrastructure, and CI/CD best practices**.

---

## 🎥 Demo

▶️ **Application Walkthrough**  
*(Click to watch the demo video)*

Malik AI Demo: https://youtu.be/2FtZxVk9Yq8

---

## 🏗️ Architecture

📌 **High-Level Architecture Diagram**  
![app](https://github.com/rjones18/Images/blob/main/Malik-AI.png)

### Architecture Overview
- Traffic enters through an **Application Load Balancer**
- Containerized Flask application runs on **Amazon ECS (Fargate)**
- Secrets are securely injected via **AWS Secrets Manager**
- AI responses are generated using the **OpenAI API**
- Application logs stream to **Amazon CloudWatch**
- Infrastructure is defined and deployed with **Terraform**

---

## ☁️ Infrastructure & IaC

- Infrastructure is provisioned using a **custom Terraform ECS module**  
  👉 https://github.com/rjones18/AWS-ECS-TERRAFORM-MODULE
- Supports:
  - Application Load Balancer
  - ECS Cluster & Services
  - IAM roles and least-privilege policies
  - Secure networking (VPC, subnets, security groups)
  - HTTPS via ACM (optional)

---

## 🔐 Security

- Secrets managed with **AWS Secrets Manager**
- HTTPS termination via **ACM**
- **Snyk** used in CI to scan Terraform/IaC for vulnerabilities
- Follows least-privilege IAM patterns

---

## 🚀 CI/CD

- Deployed using **GitHub Actions**
- Pipeline includes:
  - Terraform formatting and validation
  - Infrastructure security scanning with **Snyk**
  - Automated build and deployment to AWS ECS

---

## 🧠 AI Integration

- Uses the **OpenAI API** to generate conversational responses
- API keys securely injected at runtime via Secrets Manager
- Designed to be easily extensible for additional AI providers or models

---

## 📌 Why This Project

This project was built to showcase:
- Production-ready AWS container infrastructure
- Secure, reusable Terraform modules
- End-to-end CI/CD automation
- Practical AI integration in a real-world cloud environment

