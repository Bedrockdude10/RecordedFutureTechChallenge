# RecordedFutureTechChallenge
Tech challenge completed for Recorded Future Data Science co-op position.

# Questions from Step 3:
Here are my responses to all five questions:

---

### 1. **When looking at the list of potential lures from Step One, do you notice any patterns that will likely lead to false positives?**

Potential false positives arise from the simplicity of substring matching in domains:
- **Embedded Terms**: Terms can appear as parts of longer, unrelated strings. For instance, "mailbox" in a domain like `secure-mailbox.com` might trigger a match for "mail," even though it's not indicative of a phishing lure.
- **Legitimate Multi-Term Domains**: Domains like `gov-payments.gov` might trigger as phishing lures due to the presence of ".gov" and "paying," even though the domain is legitimate.
- **Brand Overlap**: Some terms like "gmail" or "cisco" might appear in legitimate subdomains for services collaborating with these brands.

---

### 2. **What are some of the pros/cons of using a fixed list of terms to identify these Phishing Lures?**

**Pros**:
- **Simplicity**: Easy to implement and maintain without requiring complex models or additional data.
- **Transparency**: Analysts can clearly understand and audit which terms are being monitored.
- **Performance**: Fixed lists are computationally efficient, especially when preprocessed for faster lookups.

**Cons**:
- **Static Coverage**: Fixed lists require human updates and may miss new or evolving phishing strategies that introduce novel terms.
- **False Positives and Negatives**: Domains containing legitimate uses of the terms may be flagged, while creative phishing domains using obfuscated terms may be missed.
- **Scalability**: Managing and updating the list becomes cumbersome as the scope of monitoring expands.

---

### 3. **If you were an analyst, what additional information would you need to help prioritize which lures you should investigate first?**

- **Reputation Data**: Details about the domain registrar, creation date, and DNS history to identify suspicious patterns.
- **Domain Usage**: Information about where the domain is being used, such as email campaigns, website traffic, or linked malware.
- **Keyword Context**: Insights into how the matched terms are used in the domain (e.g., standalone words vs. embedded within longer strings).
- **Threat Intelligence Feeds**: Correlation with external threat databases for known malicious domains or registrars.
- **User Reports**: Reports from end-users or customers who may have encountered phishing attempts involving the flagged domain.

---

### 4. **What would you need to refactor if asked to scale your solution to handle millions of domains, thousands of terms, and hundreds of users?**

- **Data Processing**:
  - Use streaming frameworks for real-time domain ingestion.
  - Implement batch processing for large-scale domain evaluations.

- **Efficient Term Matching**:
  - Would need to read more about how to implement it, but there could be use a trie data structure for fast term lookups across thousands of terms.

- **Notification Management**:
  - Store precomputed user hierarchies and term notifications elsewhere to reduce in-memory usage and ensure fast lookups.

- **Parallelization**:
  - Distribute domain matching and hierarchy processing across multiple worker nodes.

- **Error Handling and Logging**:
  - Add error handling & retry mechanisms and logging for each stage of the pipeline.

---

### 5. **How would you architect deploying this lure alert service? What databases, class structures, tools (queues, API’s etc.) would you think about using? Would it be a monolithic app or smaller microservices?**

- **Architecture**: I would go with a microservices architecture for better scalability and maintainability.
  - **Domain Processing Service**: A service to identify potential phishing lures.
  - **Hierarchy Management Service**: A service to manage and update user hierarchies.
  - **Notification Service**: A service to handle user notifications and subscriptions.

- **Databases**:
  - **Relational Database (PostgreSQL/MySQL)**: To store user hierarchies and subscriptions for reliable querying.
  - **NoSQL Store (MongoDB/DynamoDB)**: Maybe use to store domain metadata and match results, since metadata might change from domain to domain.

- **Tools**:
  - **Message Queues**: Use RabbitMQ or Kafka to handle asynchronous communication between services.
  - **Caching**: Use Redis for quick access to user hierarchies and precomputed term notifications.
  - **API Gateway**: Expose endpoints for important functions. Likely need to support the following:
  POST domains for lure detection
  GET user, domains[] notification pairs
  PUT terms to update the phishing terms list

- **Deployment**:
  - Deploy microservices on containerized platforms (Kubernetes?).
  - Use serverless functions for lightweight tasks like periodic term list updates.